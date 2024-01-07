import os
import yaml
import importlib
from geraldine import util
from geraldine.util import StateManager
from pprint import pprint

class GeriStateManager(StateManager):
    def __init__(self):
        super().__init__()

        self.config_file_path = os.path.join(
            os.getcwd(), 
            ".geraldine/config.yaml"
            )


        self.add_configs({
            "geri_src_dir_name" : "geri_src",
            "geri_dest_dir_name" : "geri_dist",
            "max_directory_depth" : 10,
            "priority_directories" : [
                "includes"
            ],
            "custom_plugin_directories": [
                ".geraldine/plugins"
            ],
            "descriptions":{
                "geri_src_dir_name": "The directory that will be processed",
                "geri_dest_dir_name": "The directory that processing results will be written to. It's ephemeral, make no changes to this directory, except through, the source directory.",
                "max_directory_depth": "How many directories deep the system will process.",
                "priority_directories": "These directories get processed first, in order to do things like add includes",
                "custom_plugin_directories": "Add your custom plugins in these directories, they will be used if they have a .plugin.py extension and geraldine function inside."
            }
        })

        try:
            self.config_file_exists()
            self.read_configs()
        except:
            pass

        install_dir = self.get_install_directory()
        self.add_data({
                "config_file_path": self.config_file_path,
                "root_directory": os.getcwd(),
                "install_dir": install_dir,
                "built_in_plugin_path": os.path.join(install_dir, "plugins"),
                "logger_name": "geri_log"
        })

        # need to build plugin path first
        self.add_data({
                "src_dir": os.path.join(self.data.root_directory, self.configs.geri_src_dir_name),
                "dest_dir": os.path.join(self.data.root_directory, self.configs.geri_dest_dir_name),
                "modules": self.load_modules(),
                "geraldine_directory": os.path.join(self.data.root_directory, ".geraldine")
        })

        # need src_dir 
        self.add_data({
                "priority_directories": self.build_priority_dirs()
        })

    def build_priority_dirs(self):
        priority_dirs = []
        for directory in self.configs.priority_directories:
            if os.path.isabs(directory):
                priority_dirs.append(directory)
            else:
                the_dir = os.path.join(self.data.src_dir, directory)
                priority_dirs.append(the_dir)
        return priority_dirs

    def load_modules(self):
        def load_module_from_dir(the_dir, modules):
            for module in util.depth_first_dir_walk(the_dir, max_depth=0):
                if module.name.endswith('.plugin.py'):
                    the_module = self.import_module_from_path(module.path)
                    modules[module.name[:-10]] = the_module
        modules = {}

        # load built in plugins
        load_module_from_dir(self.data.built_in_plugin_path, modules)

        # load custom plugins from config files
        for plugin_dir in self.configs.custom_plugin_directories:
            load_module_from_dir(plugin_dir, modules)

        return modules

    def get_install_directory(self):
        script_path = os.path.abspath(__file__)
        return os.path.dirname(script_path)
        
    def import_module_from_path(self, path):
        module_name = os.path.basename(path).split('.')[0]
        module_spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

    def print(self):
        print("\nDATA\n----------")
        pprint(self.data.data)
        print("\nCONFIGS\n----------")
        pprint(self.configs.data)

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

