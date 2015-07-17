import docker
import simplejson as json

def _get_redis_config(docker_client, c_id):
    inspect = docker_client.inspect_container(c_id)

    return ("redis", {}, [{"host": inspect["NetworkSettings"]["IPAddress"],
        "port": inspect["NetworkSettings"]["Ports"].keys()[0].split("/")[0]}])

MAPPING = {
    'redis': _get_redis_config
}



def _get_default_config(docker_client, c_id):
    env_variables = {v.split("=")[0].split("datadog_")[1]: v.split("=")[1] for v in docker_client.inspect_container(c_id)['Config']['Env'] if v.split("=")[0].startswith("datadog_")}
    check_name = None
    init_config = None
    instances = None
    if "check_name" not in env_variables:
        return None

    check_name = env_variables["check_name"]
    del env_variables["check_name"]

    if "init_config" in env_variables:
        init_config = json.loads(env_variables["init_config"])
        del env_variables["init_config"]

    if "instances" in env_variables:
        instances = json.loads(env_variables["instances"])

    else:
        instances = [{k:v} for k,v in env_variables.iteritems()]
    
    return (check_name, init_config, instances)




def get_configs():
    docker_client = docker.Client(base_url='unix://var/run/docker.sock', version="1.18")
    containers = [(c['Image'].split(":")[0], c['Id']) for c in docker_client.containers()]
    configs = {}

    for image, c_id in containers:
        if image in MAPPING:
            conf = MAPPING[image](docker_client, c_id)
        else:
            conf = _get_default_config(docker_client, c_id)
        if conf is not None:
            configs[conf[0]] = (conf[1], conf[2])

    return configs