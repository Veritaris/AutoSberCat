# Auto Sber Cat

Well, this a scripts bunch to automate SberCat app at VKontakte
Usage:

1. Install poetry for python
2. Clone repo to any place you want
3. Rename `.env.local` file to `.env`
4. Open Dev console while at VK app page, that in Network tab find request like https://sbercat-shelter.ru-prod2.kts.studio/api/user/auth?XXX.
   Open its response, copy token value and past as `SBERCAT_APP_TOKEN`
5. Install dependencies and activate virtual environment

   ```bash
   poetry config virtualenvs.in-project true
   poetry env use 3.10
   source .venv/bin/activate
   poetry install
   export $(cat .env | xargs)
   ```

6. Run and check if your kotany really updated

   ```bash
   python -m app.SberCatClient
   ```

7. If yes - create kinda of cron or whatever you want to run this cript inside venv

Future improvements:

- [ ] Background scheduler based on celery / threads
- [ ] Autobuy of new employers if available
- [ ] Pizza & wall sticker autobuy to speed up kotans
- [x] Money auto transfer to private card to increase money income with payday
- [ ] Add pool of clients to work over several accounts
- [ ] Auto token renew by vk oauth
