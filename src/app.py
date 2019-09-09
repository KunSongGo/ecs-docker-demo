import time

from flask import Flask

app = Flask(__name__)



@app.route('/')
def hello():
    return '<!DOCTYPE html> \
<html lang="en"> \
<head> \
<title>Page Title</title> \
<meta charset="UTF-8"> \
<meta name="viewport" content="width=device-width, initial-scale=1"> \
<style> \
 \
 \
/* Header/logo Title */ \
.header { \
  padding: 80px; \
  text-align: center; \
  background: #1abc9c; \
  color: white; \
} \
 \
/* Increase the font size of the heading */ \
.header h1 { \
  font-size: 40px; \
} \
 \
 \
</style> \
</head> \
<body> \
<div class="header"> \
  <h1>ECS Fargate demo website</h1> \
  <p>A <b>simple hello</b> from ECS Fargate</p> \
</div> \
</body> \
</html>  '  
