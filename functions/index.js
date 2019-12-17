// [START functionsimport]
const functions = require('firebase-functions');
// [END functionsimport]
// [START additionalimports]
// The Firebase Admin SDK to access the Cloud Firestore.
const admin = require('firebase-admin');
const axios = require('axios');
const seatingHelper = require('./seatingHelper');
const config = require('../config');

// CORS Express middleware to enable CORS Requests.
const cors = require('cors')({
  origin: true,
});
// [END additionalimports]

// [START admininitialize]
admin.initializeApp();
// [END admininitialize]

function saveCommand(channel, action, email) {
  const newCommand = {
    channel,
    action,
    email,
    timestamp: admin.firestore.Timestamp.fromDate(new Date()),
  };

  const commandRef = admin.firestore().collection('commands').doc()

  return commandRef.set(newCommand);
}

// [START all]

// [START trigger]
exports.command = functions.https.onRequest((req, res) => {
  // [END trigger]

  // [START usingMiddleware]
  // Enable CORS using the `cors` express middleware.
  return cors(req, res, async () => {
    // [END usingMiddleware]

    // [START readQueryParam]
    const channel = req.query.channel;
    const action = req.query.action;
    const email = req.query.email || '';
    // const email = context.auth.token.email || '';
    // [END readQueryParam]

    try {
      // [START adminSdkAdd]
      const writeResult = await saveCommand(channel, action, email);
      // [END adminSdkAdd]

      // [START sendResponse]
      res.json({ commands, writeResult });
      // [END sendResponse]
    } catch (error) {
      // [START sendErrorResponse]
      res.json({ commands, writeResult: null });
      // [END sendErrorResponse]
    }
  });
});

// [START trigger]
exports.setCommand = functions.https.onCall(async (data, context) => {
  // [END trigger]

  // verify Firebase Auth ID token
  if (!context.auth) {
    // [START sendError]
    return { message: 'Authentication Required!', code: 401 };
    // [END sendError]
  }

  // [START readQueryParams]
  const email = context.auth.token.email || '';
  const channel = data.channel;
  const action = data.action;
  // const doc = data.doc;
  // console.log('doc', doc);
  // [END readQueryParams]

  try {
    // [START adminSdkAdd]
    const writeResult = await saveCommand(channel, action, email);
    // [END adminSdkAdd]

    // [START sendResponse]
    return { message: 'ok', code: 200 };
    // [END sendResponse]
  } catch (error) {
    // [START sendErrorResponse]
    console.log(error);

    return { message: error, code: 500 };
    // [END sendErrorResponse]
  }
});

exports.setAlexaCommand = functions.https.onRequest((req, res) => {
  return cors(req, res, async () => {
    if (req.body.auth_token !== '3a081d8d4cd1ee3ef0fc617636b5634e9635fabb') {
      return res.status(401).json({message:'Authentication Required!'});
    }

    const { email, action, channel } = req.body;

    try {
      const writeResult = await saveCommand(channel, action, email);
    } catch (err) {
      return res.status(400).json({messge: 'Internal Error', err});
    }

    return res.status(200).json({messge: 'ok'});
  });
});

exports.refreshSeating = functions.https.onCall(async (data, context) => {
  const seats = await axios(config.officeSpaceSeatsUrl, {
    method: 'GET',
    headers:{
      'Content-Type': 'application/json',
      'authorization': `Token token="${config.officeSpaceAPIToken}"`,
    }
  });

  const occupiedSeatsMappedOnPod = seats.data.response.map(seat => {
    seat.channel = seatingHelper.detectPod(seat.coordinates);
    return seat;
  });

  const promises = occupiedSeatsMappedOnPod
    .filter(seat => seat && seat.occupancy && seat.occupancy.employee_url)
    .map((seat) => {
      return axios(config.officeSpaceUrl + seat.occupancy.employee_url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'authorization': `Token token="${config.officeSpaceAPIToken}"`,
        }
      })
        .then(employee => {
          seat.email = employee.data.response.email;
          return seat;
        })
        .catch((err) => {
          console.log(err.response.statusText, seat.id);
        });
    });

  Promise.all(promises)
    .then(responses => {
    // Some seats have employee url, but there is no employee for that and on request we get 404. Then error is thrown and undefined is returned.
    admin.firestore()
      .collection('employees')
      .doc('vilnius')
      .set({
        seats: responses.filter(r => typeof r !== 'undefined'),
      })
      .catch(err => console.log(err));

    return true;
  })
    .catch((err) => {
      console.log(err);
    });

});
// [END all]
