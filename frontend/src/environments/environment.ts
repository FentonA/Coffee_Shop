/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: true,
  apiServerUrl: 'https://127.0.0.1:5000/login', // the running FLASK api server url
  auth0: {
    url: 'dev-hnsuo', // the auth0 domain prefix
    audience: 'shop_login', // the audience set for the auth0 app
    clientId: 'MW6Be2ImhM8OkPjjaU8VAdETPzLodtrA', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100/tabs/drink-menu', // the base url of the running ionic application. 
  }
};
