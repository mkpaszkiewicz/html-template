HTML template parser
--------------------

### Description

The module contains implementation of CSV to HTML template parser. Template is based on [Jinja2](http://jinja.pocoo.org/) templates, widely used in Django, Flask and other web frameworks.

### Example

**data.csv:**
```
firstname, lastname, salary, age
Brad, Smith, 2500.00, 34
Will, Pitt, 3000.00, 42
Jennifer, Polez, 100.00, 17
```

**template:**
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
    {% for row in csv %}
        {% if row.age > 18 %}
            {{ name_li(row.firstname, row.lastname) }}
        {% endif %}
    {% endfor %}
    </ul>
    <h1>My Webpage</h1>
    <span>{{ csv[1].age + csv[2].age }}</span>

    {# a comment #}
</body>
</html>
```

**Generated HTML:**
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
