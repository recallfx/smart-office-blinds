// [START functionsimport]
const functions = require('firebase-functions');
// [END functionsimport]
// [START additionalimports]
// The Firebase Admin SDK to access the Cloud Firestore.
const admin = require('firebase-admin');

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
exports.setChannelStatus = functions.https.onRequest((req, res) => {
  // [END trigger]

  // [START usingMiddleware]
  // Enable CORS using the `cors` express middleware.
  return cors(req, res, async () => {
    // [END usingMiddleware]

    // [START readQueryParam]
    const channel = req.query.channel;
    const status = req.query.status;
    const action = req.query.action || null;
    // [END readQueryParam]

    try {
      const channelDocRef = admin.firestore().collection('channels').doc(channel);

      channelDocRef.get()
        .then(doc => {
          const writeResult = channelDocRef.set(
            {
              status: status
            },
            {
              merge: true
            }
          );

          res.json({ writeResult });
        })
        .catch(err => {

        });

    } catch (error) {
      // [START sendErrorResponse]
      res.json({ writeResult: null });
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

// [END all]
