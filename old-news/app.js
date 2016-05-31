/**
 * This basic node.js script authorizes a user with Spotify and
 * exposes the access token for other programs to grab.
 * 
 * Adapted from the simple authorization tutorial at developer.spotify.com
 * Nick Speal, 2016
 */

var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var querystring = require('querystring');
var cookieParser = require('cookie-parser');

var client_id = '338af3083e4e4069960c77b6978cb7a5'; // Your client id
var client_secret = '9beb594d85ce466a9bf208de1f89aad3'; // Your client secret
var redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri

var ACCESS_TOKEN_GLOBAL = null
var REFRESH_TOKEN_GLOBAL = null
/**
 * Generates a random string containing numbers and letters
 * @param  {number} length The length of the string
 * @return {string} The generated string
 */
var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

var stateKey = 'spotify_auth_state';

var app = express();

app.use(express.static(__dirname + '/public'))
   .use(cookieParser());

app.get('/login', function(req, res) {
  ACCESS_TOKEN_GLOBAL = null //reset these if the user is newly logging in.
  REFRESH_TOKEN_GLOBAL = null

  var state = generateRandomString(16);
  res.cookie(stateKey, state);

  // your application requests authorization
  var scope = 'user-read-private user-read-email playlist-modify-private'; 
  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }));
});

app.get('/callback', function(req, res) {
  // your application requests refresh and access tokens
  // after checking the state parameter

  var code = req.query.code || null;
  var state = req.query.state || null;
  var storedState = req.cookies ? req.cookies[stateKey] : null;

  if (state === null || state !== storedState) {
    res.redirect('/#' +
      querystring.stringify({
        error: 'state_mismatch'
      }));
  } else {
    res.clearCookie(stateKey);
    var authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      form: {
        code: code,
        redirect_uri: redirect_uri,
        grant_type: 'authorization_code'
      },
      headers: {
        'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
      },
      json: true
    };
    
    //Ask Spotify /api/token for user access token, and then save the response:
    request.post(authOptions, function(error, response, body) {
      if (!error && response.statusCode === 200) {
        console.log('Got token from Spotify.');
        ACCESS_TOKEN_GLOBAL = body.access_token;
        REFRESH_TOKEN_GLOBAL = body.refresh_token;            

      } else {
        res.redirect('/#' +
          querystring.stringify({
            error: 'invalid_token'
          }));
      }
    });
  }
});


app.get('/refresh_token', function(req, res) {
  // requesting access token from refresh token
  var refresh_token = req.query.refresh_token;
  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  };

  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === 200) {
      var access_token = body.access_token;
      res.send({
        'access_token': access_token
      });
    }
  });
});


app.get('/check_credentials', function(req, res) {
  // python script asks JS server for the spotify credentials
  if (ACCESS_TOKEN_GLOBAL === null) {
    res.status(204).send('Waiting for access token'); //nocontent
  } else {
    console.log('Sending client the access token');
    res.send({'access_token': ACCESS_TOKEN_GLOBAL, 'refresh_token': REFRESH_TOKEN_GLOBAL});
  }
});

app.get('/kill', function(req, res) {
  // Kill self if python asks me to
  console.log('Received kill command');
  process.exit(1);
});

console.log('Listening on 8888');
app.listen(8888);
