from pyramid.view import view_config
from pyramid.response import Response
from proj.app.utils.exceptions import InvalidAuthorization, AuthenticationError, HttpWrongResonse


@view_config(context=AssertionError)
def assertionerror(exc, request):
    msg = exc.args[0] if exc.args else "e:01 something is not right please try again"
    return Response(json={"error": msg}, status=400)


@view_config(context=ValueError)
def valueerror(exc, request):
    msg = exc.args[0] if exc.args else "e:02 something is not right please try again"
    return Response(json={"error": msg}, status=503)


@view_config(context=KeyError)
def keyerror(exc, request):
    msg = exc.args[0] if exc.args else "e:03 something is not right please try again"
    return Response(json={"error": msg}, status=503)


@view_config(context=IndexError)
def indexerror(exc, request):
    msg = exc.args[0] if exc.args else "e:04 something is not right please try again"
    return Response(json={"error": msg}, status=503)


@view_config(context=InvalidAuthorization)
def invalid_authorization(exc, request):
    msg = exc.args[0] if exc.args else "e:05 you are not authorized to perform this operation"
    return Response(json={"error": msg}, status=403)


@view_config(context=AuthenticationError)
def authentication_error(exc, request):
    msg = exc.args[0] if exc.args else "e:06 the request requires authentication"
    return Response(json={"error": msg}, status=403)


@view_config(context=HttpWrongResonse)
def http_wrong_response(exc, request):
    msg = exc.args[0] if exc.args else "e:07 unexpected response from service "
    return Response(json={"error": msg}, status=403)