# Geraldine: a static component generator

* Do you have a bunch of JSON or YAML or TOML you want to convert to html components to keep your browser code clean?

* Geraldine converts string templates with front matter into html:



```
(/somedir/components/geri_src/helloworld/mytemplate.jinja.html)
---
processer: jinja_parser 
json_path: /somedir/data/myjson.json
---
<div> {{some_variable}}</div>

```

```
(/somedir/data/myjson.json)
{
    "some_variable":"hello world"
}
```

* run `geri` in `/somedir/components` and get output:

```
(/somedir/components/dist/helloworld/mytemplate.html)
<div>hello world</div>
```

* Geri iterates through every directory underneath the `geri_src` in which it was run and rebuilds the directory structure in the sibling `dist` folder.
    * (has a max depth of 10, but can be changed if needed in the source code)
* If it encounters a file with front matter geri will parse the front matter with the json specified in the example. If no front matter the file will be copied exactly. 


## Examples
* see [./geraldine/examples](./geraldine/examples) 

## Install

### Via pypi
* Pypi is currently locked to new users due to some suspicious stuff going on.

### Via wheel (best way)
* You can pip3 install the wheel file from the dist folder and start using `geri` command.
    * `pip3 install geraldine-0.1.0-py3-none-any.whl`

### The long way
1. Clone the repo
2. Install the dependencies in requirements.txt (create a venv if you want)
    * will have to put a bash script in the /bin folder to activate the venv and run the geri command or remember to activate it
3. Add the /bin folder to the path
4. Start using Geraldine with the `geri` command

### Use Poetry
* `poetry install`
* `poetry run python3 cli.py -h`

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

* The name of the plugin will be set in the `processer` field in the front matter

* The plugin needs a top level function with the name `geraldine` that gets called by the main system.


* The data passed to geraldine(data) function looks like this:
```
{   
    'destination_path': '/tmp/geri_test/dist/test1/test.jinja.html',
    'frontmatter': {   'extension': 'html',
                       'filename_key': 'class.0.name',
                       'json_path': '/home/nick/bash_shortcuts/in_prog/char_gen/data/json/classes/all_classes.json',
                       'processor': 'jinja_file_parser'},
    'src_path': '/tmp/geri_test/geri_src/test1/test.jinja.html',
    'template_content': '<div>{{class.name}}</div>\n\n',
    'template_filename': 'test.jinja.html'
}

```

* What ever you return from the function will be written to the output file in destination folder
* If you return nothing, no file will be written as it's assumed you're creating the file within the plugin yourself.
* Declare a top level variable to remove an extension from the file name: remove_extensions=['jinja'] 


## To Do:
* Stick it up on pypi to make it installable with pip
* Make a user folder: ~/.geraldine 
    * config file for declaring custom things like max-depth, input/output dir, etc.
    * folder for custom plugins
* Refactor post processing block into it's own spot
* Implement yaml and toml processors
* Better docs with examples
* File watching
* Tests