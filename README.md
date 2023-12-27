# Geraldine: a static component generator

* Do you have a bunch of JSON or YAML or TOML you want to convert to html components to keep your browser code clean?

* Geraldine converts string templates with front matter into html:


```
/somedir/components/geri_src/helloworld/mytemplate.jinja.html


---
jinja_parser: /somedir/data/myjson.json
---
<div> {{some_variable}}</div>

```

```
/somedir/data/myjson.json


{
    "some_variable":"hello world"
}
```

* output:
/somedir/components/dist/helloworld/mytemplate.html

```
<div>hello world</div>
```


* run: `geri` in `/somedir/components` directory to make this happen

* Geri iterates through every directory underneath the `geri_src` in which it was run and rebuilds the directory structure in the sibling `dist` folder.
    * (has a max depth of 10, but be careful!)
* If it encounters a file with front matter geri will parse the front matter with the json specified in the example. If no front matter the file will be copied exactly. 

## Install
1. Clone the repo
2. Install the dependencies in requirements.txt (create a venv if you want)
3. Add the /bin folder to the path
4. Start using Geraldine with the `geri` command

* One day I will put this on pypi

## CLI
```bash
geri
    Build Completed Successfully

geri -h
    usage: geri [-h] [-i] [-p]

    Geraldine, a static component generator.

    options:
    -h, --help     show this help message and exit
    -i, --info     Show install location
    -p, --plugins  List available plugins


geri --plugins
    Available plugins:
    jinja_parser.plugin.py
    jinja_file_parser.plugin.py

geri --info
    install location: /home/nick/Projects/in_prog/geraldine/geraldine
    plugin path: /home/nick/Projects/in_prog/geraldine/geraldine/plugins

```



## Plugins

* Geri is built with a plugin system, so if you want to create a plugin just drop it into the plugin path with extension: .plugin.py 

* see plugin folder: [./geraldine/plugins](./geraldine/plugins)

* The name of the plugin will be the key you call in the front matter

* The plugin needs a top level function with the name `geraldine` that gets called by the main system.

The three parameters passed are:
1. In the key value pair in the front matter this is the value
    * i.e. the location of json paths or anything else
    * can be any data structure like list or dict, geri just punts it from the front matter to the function untouched
2. The path of template on the system
    * useful for having a base to locate data source files
3. The raw content being parsed
    * Basically: the template with the front matter removed

```
def geraldine(value_from_front_matter, template_path, template_content):
    ....
```


* What ever you return from the function will be written to the file
* If you return nothing, no file will be written as it's assumed you're creating the file yourself.
* declare a top level variable to remove an extension from the file name: remove_extensions=['jinja'] 


## To Do:
* Stick it up on pypi to make it installable with pip
* make cli options for defining input and output dirs?
* config file for declaring custom things like max-depth input/output dir?
* make an external folder for custom plugins
* refactor post processing block into it's own spot
* Implement yaml and toml parsing