import os
import yaml
from geraldine.util import ConfigManager

class GeriConfigManager(ConfigManager):
    def __init__(self):
        super().__init__()

        self.config_file_path = os.path.join(
            os.getcwd(), 
            ".geraldine/config.yaml"
            )

        self.add_nonwrite_configs(
            {"config_file_path": self.config_file_path}
        )

        self.add_configs({
            "geri_src_dir_name" : "geri_src",
            "geri_dest_dir_name" : "geri_dir",
            "max_directory_depth" : 10,
            "priority_directories" : [
                "includes"
            ],
            "custom_plugin_directories": [
                ".geralding/plugins"
            ],
            "descriptions":{
                "geri_src_dir_name": "the directory that will be processed",
                "geri_dest_dir_name": "the directory that processing results will be written to. It's ephemeral, make no changes here, except through, the source directory.",
                "max_directory_depth": "how many directories deep the system will process.",
                "priority_directories": "The directories get processed first, in order to do things like add includes",
                "custom_plugin_directories": "add your custom plugins in these directories, they will be used if they have a .plugin.py extension and geraldine function inside."
            }
        })

        try:
            self.config_file_exists()
            self.read_configs()
        except:
            pass


    # def init_system(self):
    #     self.geri_root_dir = os.getcwd()
    #     cwd = self.geri_root_dir
    #     self.source_dir =  os.path.join(cwd, self.geri_source_dir_name)
    #     self.destination_dir = os.path.join(cwd, self.geri_dest_dir_name)

    # def create_geri_src_directories(self):
    #     # create source dir
    #     util.create_dir(source_dir)
    #     # create geraldine dir
    #     util.create_dir(os.path.join(cwd, '.geraldine'))
    #     # create config file
    #     config_seed_file = util.get_file_in_wheel('geraldine', 'seed_config_file.yaml')
    #     util.write_file(os.path.join(cwd, '.geraldine', 'config.yaml'), config_seed_file)
    #     # create plugin directory
    #     util.create_dir(os.path.join(cwd, '.geraldine', 'plugins'))
    
    # def get_info(self):
    #     return {
    #         "install location" : script_dir,
    #         "plugin path" : plugin_path,
    #         "destination dir" : destination_dir
    #     }

    # def list_plugins(self):
    #     files = [f for f in os.listdir(plugin_path) 
    #         if os.path.isfile(os.path.join(plugin_path, f))]
    #     return files

