from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gotrue.exceptions import APIError
from starlette.middleware.sessions import SessionMiddleware
from supabase import Client, create_client

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key='secret_key')

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

supabase: Client = create_client('https://cwusefvlawmktalzqxth.supabase.co',
                                 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3dXNlZnZsYXdta3RhbHpxeHRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY2NjU2MzI4MywiZXhwIjoxOTgyMTM5MjgzfQ.McOLluI5GBqnZv7VbHJJQ2VgwJ6Ua5ATGEetWzm_0LI')


def get_user(request: Request):
    if (request.session.get('access_token')):
        access_token = request.session['access_token']
        try:
            return supabase.auth.api.get_user(jwt=access_token)
        except APIError:
            return False
    else:
        return False


@app.get('/', response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_user)):
    users = supabase.auth.api.list_users()

    # colors = supabase.table('colors').select('color').execute()

    # total = Counter(colors.data)

    # print(dict((x.color, x) for x in colors.data.items()))
    return templates.TemplateResponse('index.html', {'request': request, 'users': users, 'user': user})


@app.get('/login')
async def login(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})


@app.get('/auth-login')
async def auth_login(provider: str):
    google_auth_url = supabase.auth.sign_in(
        provider=provider, redirect_to='http://localhost:8000/token')

    return RedirectResponse(google_auth_url, status_code=302)


@app.get('/profile', response_class=HTMLResponse)
async def profile(request: Request, user=Depends(get_user)):

    if not (user):
        return RedirectResponse('/login', status_code=302)
    else:
        return templates.TemplateResponse('profile.html', {'request': request, 'user': user})


@app.get('/token', response_class=HTMLResponse)
async def token(request: Request):

    return templates.TemplateResponse('token.html', {'request': request})


@app.get('/verify')
async def verify(request: Request):

    access_token = request.headers['access_token']
    request.session['access_token'] = access_token

    return True


@app.post('/color')
async def color(color: str, user=Depends(get_user)):

    has_color = supabase.table('colors').select('color').eq(
        'user', str(user.id)).execute()

    if (has_color):
        data = supabase.table('colors').update({'color': color}).eq(
            'user', str(user.id)).execute()
        return data
    else:
        data = supabase.table('colors').insert(
            {'user': str(user.id), 'color': color}).execute()
        return data
