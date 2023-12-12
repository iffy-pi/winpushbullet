import keyring
CRED_SERVICE_NAME = "PushBullet-Access-Token"
CRED_USER_NAME = "PC-PushBullet-Integration"

if __name__ == "__main__":
	accessToken = input('Paste PushBullet Access Token: ').strip()

	keyring.set_password(
		CRED_SERVICE_NAME,
		CRED_USER_NAME,
		accessToken
		)

	print('Access Token has been saved as a Generic Windows Credential.')
	print(f'Service Name: {CRED_SERVICE_NAME}')
	print(f'Username: {CRED_USER_NAME}')
