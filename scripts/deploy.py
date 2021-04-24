#! /usr/local/bin/python3

import argparse
import datetime
import glob
import json
import os
import shutil
import boto3
import zipfile
import subprocess

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
api_client = boto3.client('apigateway')
cfn_client = boto3.client('cloudformation')
log_client = boto3.client('logs')
stack_name = "stunning-disco"
web_src_bucket = os.environ.get('WEB_SRC_BUCKET')


def arguments():
    parser = argparse.ArgumentParser(description='Parameterized deployment script for Stunning-Disco.')
    parser.add_argument('--lambdas',    '-l',  help='Deploy lambda code.', action='store_true')
    parser.add_argument('--layers',     '-y',  help='Deploy lambda layers.', action='store_true')
    parser.add_argument('--web',        '-w',  help='Deploy front-end web-resources.', action='store_true')
    parser.add_argument('--sam',        '-s',  help='Package and deploy SAM template.', action='store_true')
    parser.add_argument('--api',        '-g',  help='Deploy API Gateway stage.', action='store_true')
    parser.add_argument('--all',        '-a',  help='Deploy all resources.', action='store_true')
    parser.add_argument('--delete',     '-d',  help='Delete existing stack resources.', action='store_true')
    parser.add_argument('--debug',      '-o',  help='Enable debugging output.', action='store_true')
    return parser.parse_args()


def deploy_web_resource(debug=False):
    web_src_files = glob.glob(f'src/*')
    for file_path in web_src_files:
        file_name = file_path.split('/')[-1]
        s3_client.upload_file(file_path, web_src_bucket, file_name)
        if debug:
            print(f"Deployed resource with path: {file_path}, name: {file_name}")
    print("Web resources uploaded.")


def zip_lambda_resources(debug=False):
    lambda_src_files = glob.glob(f'lambdas/*')
    if debug: print(f"lambda_src_files: {lambda_src_files}")
    lambda_zip_files = []
    for lambda_source_path in lambda_src_files:
        lambda_file_name = lambda_source_path.split('/')[-1]
        lambda_zip_name = f'{lambda_file_name.split(".py")[0]}.zip'
        with zipfile.ZipFile(lambda_zip_name, 'w') as lambda_function_zip:
            lambda_function_zip.write(lambda_source_path, arcname=lambda_file_name)
        lambda_zip_files.append(lambda_zip_name)
    print(f"Zipped lambda resources: {lambda_zip_files}")
    return lambda_zip_files


def deploy_lambda_layers(debug=False):
    lambda_layers = glob.glob(f'layers/*')
    print(f"Packaging lambda layers: {lambda_layers}")
    for layer in lambda_layers:
        layer_name = layer.split('/')[-1]

        os.mkdir(f"{layer}/python")

        package_cmd = f"python3 -m pip install -t {layer}/python {layer_name}".split(' ')
        result = subprocess.run(package_cmd, capture_output=True)
        if result.returncode != 0 or result.stderr:
            print(result.stderr.decode("utf-8"))
        elif debug:
            print(result.stdout.decode("utf-8"))
        print(f"Successfully packaged {layer}.")

        result_zip = f"{layer_name}_layer"
        shutil.make_archive(result_zip, 'zip', f"{layer}")
        s3_client.upload_file(f"{result_zip}.zip", "vizzyy-packaging", f"{result_zip}.zip")
        shutil.rmtree(f"{layer}/python")

        # file_bytes = open(f"{result_zip}.zip", 'rb').read()
        # response = lambda_client.publish_layer_version(
        #     LayerName=result_zip,
        #     Description=result_zip,
        #     Content={
        #         'ZipFile': file_bytes
        #     },
        #     CompatibleRuntimes=['python3.8'],
        # )
        # if debug: print(response)

        print(f"Successfully deployed {result_zip}.")
        os.remove(f"{result_zip}.zip")

    return lambda_layers


def delete_lambda_layers(debug=False):
    lambda_layers = glob.glob(f'layers/*')
    print(f"Deleting lambda layers: {lambda_layers}")
    for layer in lambda_layers:
        layer_name = layer.split('/')[-1] + "_layer"
        layer_versions = lambda_client.list_layer_versions(
            LayerName=layer_name,
        )["LayerVersions"]
        if debug: print(layer_versions)
        for layer_version in layer_versions:
            version_num = layer_version["Version"]
            response = lambda_client.delete_layer_version(
                LayerName=layer_name,
                VersionNumber=version_num
            )
            if debug: print(response)
            print(f"Deleted {layer_name} version {version_num}")


def deploy_lambda_resources(debug=False):
    lambda_zip_files = zip_lambda_resources()

    for lambda_source_path in lambda_zip_files:
        lambda_zip_name = lambda_source_path.split('/')[-1]
        lambda_function_name = lambda_zip_name.split(".zip")[0]
        with open(lambda_zip_name, "rb") as lamda_zip:
            response = lambda_client.update_function_code(
                FunctionName=lambda_function_name,
                ZipFile=lamda_zip.read(),
                Publish=True,
            )
            if debug:
                print(f"update_function_code: source_path: {lambda_source_path}, "
                      f"function: {lambda_function_name}, response: {json.dumps(response, indent=2)}")

    print("Deployed lambda resources.")
    delete_lambda_zips(lambda_zip_files)


def delete_lambda_zips(lambda_zips):
    for file in lambda_zips:
        os.remove(file)
    print("Deleted lambda zip files.")


def get_rest_api(api_name):
    response = api_client.get_rest_apis()
    for api in response["items"]:
        if api["name"] == api_name:
            return api

    print(f"get_rest_api({api_name}) returned None.")
    return None


def deploy_gateway_stage(debug=False):
    api_data = get_rest_api(stack_name)
    response = api_client.create_deployment(
        restApiId=api_data["id"],
        stageName='Prod',
    )
    if debug: print(f"create_deployment: api_data: {api_data}, response: {json.dumps(response, indent=2, default=str)}")
    print(f"Deployed gateway stage.")


def delete_cfn_resources(debug=False):
    api_data = get_rest_api(stack_name) # Needs to go before stack is deleted

    response = cfn_client.delete_stack(StackName=stack_name)
    print(f"Initiated stack deletion for {stack_name}.")
    if debug: print(f"delete_stack response: {response}")

    stack_delete_waiter = cfn_client.get_waiter('stack_delete_complete')
    print(f"Waiting on deletion of {stack_name}...")
    stack_delete_waiter.wait(StackName=stack_name)
    print(f"Successfully deleted stack {stack_name}.")

    if api_data is not None:
        api_id = api_data["id"]
        log_group = f"API-Gateway-Execution-Logs_{api_id}/Prod"
        response = log_client.delete_log_group(logGroupName=log_group)
        if debug: print(f"Deleted log group: {log_group}, response: {response}")


def deploy_sam_resources(debug=False):
    zip_files = zip_lambda_resources()

    print("Deploying SAM resources.")
    deploy_cmd = f"sam deploy --resolve-s3 --stack-name {stack_name} " \
                 f"--capabilities CAPABILITY_IAM --no-fail-on-empty-changeset".split(' ')
    result = subprocess.run(deploy_cmd, capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
    elif debug:
        print(result.stdout.decode("utf-8"))
    else:
        print("SAM deploy successful.")

    delete_lambda_zips(zip_files)


if __name__ == "__main__":
    start = datetime.datetime.now()
    args = arguments()

    # Order kind of matters here -- if we're gonna delete we want it to be first
    if args.delete:
        delete_cfn_resources(args.debug)
        delete_lambda_layers(args.debug)
    if args.web or args.all:
        deploy_web_resource(args.debug)
    if args.sam or args.layers or args.all:
        deploy_lambda_layers(args.debug)
    if args.sam or args.all:
        deploy_sam_resources(args.debug)
    elif args.lambdas or args.all:
        deploy_lambda_resources(args.debug)
    if args.api or args.sam or args.all:
        deploy_gateway_stage(args.debug)

    print(f"Script finished in {datetime.datetime.now() - start}")
