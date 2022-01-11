# testp

####Get inside the workdir i.e testp. you can create a virtualenv or use your main installation version should be at least 3.7.3
* To create a virtualenv 

        virtualenv -p python3 <name of you env>
* activate your virtual environment

        source <name of you env>/bin/activate
* Install the dependencies.

        pip install -r requirements.txt

* Work out your system dependencies. 
 
## web-server
    python __init__.py
###### By default the server will be available under 
    http://localhost:8443

```
N.B. 
1. this project depends on postgresql database the connection parameters are defined in proj/app/settings.py
2. the database can be populated using the `populate` function instide proj/app/dbops/script.py
3. The JWT token creation and validation requires generating the certificates first uncomment the code block in 
proj/auth/certs.py first time you run the server or create the token.
3. to create a token use the function create_token in proj/auth/jwt_util.py make sure you pass `admin` as one of the roles
4. the generated token can then be passed as a custom http header `X-AUTH` for api requests
```