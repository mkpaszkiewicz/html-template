HTML template parser
--------------------

### Description

The module contains implementation of HTML template parser. Template is based on [Jinja2](http://jinja.pocoo.org/) templates, widely used in Django, Flask and other web frameworks.
Parser accepts CSV, JSON, YAML data models.

### Requirements and installation

Module requires python3.X
To install all dependencies run:
```
$ python setup.py install
```

### Tests

All tests are located in ```tests``` directory. To execute them run:

```
$ python tests
```

### Example

```
$ ./gen_html -c data.csv -t input.html -o output.html
```

To see help page and description of particular arguments add ```-h``` or ```--help```

**model:** model.csv
```
firstname, lastname, salary, age
Brad, Smith, 2500.00, 34
Will, Pitt, 3000.00, 42
Jennifer, Polez, 100.00, 17
```

**template:** input.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Webpage</title>
</head>
<body>
    {% macro name_li(firstname, lastname) %}
        <li>Name: {{ firstname }} {{ lastname }}</li>
    {% endmacro %}
    {% set variable = 'Names' %}
    <span>{{ variable }}</span>
    <ul id="names">
    {% for row in model %}
        {% if row.age > 18 %}
            {{ name_li(row.firstname, row.lastname) }}
        {% endif %}
    {% endfor %}
    </ul>
    <h1>My Webpage</h1>
    <span>{{ model[1].age + model[2].age }}</span>

    {# a comment #}
</body>
</html>
```

**Generated HTML:** output.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Webpage</title>
</head>
<body>
    <span>Names</span>
    <ul id="names">
        <li>Name: Brad Smith</li>
        <li>Name: Will, Pitt</li>
    </ul>
    <h1>My Webpage</h1>
    <span>59</span>
</body>
</html>
```

### Author
Marcin K. Paszkiewicz<br>
*Warsaw University of Technology*
