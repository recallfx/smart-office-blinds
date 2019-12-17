import { availableApiTokens, adminEmails } from '../../config.json';
import { databaseCollections, dataCollectionDocuments } from '../../constants';
import getMappedUsers from './office-space';

const functions = require('firebase-functions');
const admin = require('firebase-admin');

const authenticationRequiredResponseObject = {
  message: 'Authentication Required!',
  code: 401,
};
const internalErrorResponseObject = { message: 'Internal Error', code: 400 };
const serverErrorResponseObject = { message: 'Server Error', code: 500 };
const okResponseObject = { message: 'OK', code: 200 };

// CORS Express middleware to enable CORS Requests.
const cors = require('cors')({ origin: true });

admin.initializeApp();

function logMessage(message) {
  console.log(message);
}

function logException(message) {
  console.error(message);
}

function saveCommand(channel, action, email) {
  const newCommand = {
    channel,
    action,
    email,
    timestamp: admin.firestore.Timestamp.fromDate(new Date()),
  };

  const commandRef = admin
    .firestore()
    .collection(databaseCollections.commands)
    .doc();

  return commandRef.set(newCommand);
}

exports.setChannelStatus2 = functions.https.onRequest((req, res) => {
  return cors(req, res, async () => {
    if (!availableApiTokens.includes(req.body.auth_token)) {
      return res.status(401).json(authenticationRequiredResponseObject);
    }

    const { channel, status, action = null } = req.query;

    try {
      const channelDocRef = admin
        .firestore()
        .collection(databaseCollections.channels)
        .doc(channel);
      const doc = await channelDocRef.get();

      let params = {
        status: status,
      };

      if (action !== null) {
        params.last_action = action;
      }

      await channelDocRef.set(params, { merge: true });

      return res.status(200).json(okResponseObject);
    } catch (error) {
      return res
        .status(400)
        .json(Object.assign({}, internalErrorResponseObject, { error }));
    }
  });
});

exports.setAlexaCommand2 = functions.https.onRequest((req, res) => {
  return cors(req, res, async () => {
    if (!availableApiTokens.includes(req.body.auth_token)) {
      return res.status(401).json(authenticationRequiredResponseObject);
    }

    const { email, action, channel } = req.body;

    try {
      await saveCommand(channel, action, email);

      return res.status(200).json(okResponseObject);
    } catch (error) {
      logException(error);

      return res
        .status(400)
        .json(Object.assign({}, internalErrorResponseObject, { error }));
    }
  });
});

exports.setCommand2 = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    return authenticationRequiredResponseObject;
  }

  const email = context.auth.token.email || '';
  const channel = data.channel;
  const action = data.action;

  try {
    await saveCommand(channel, action, email);

    return okResponseObject;
  } catch (error) {
    logException(error);

    return Object.assign({}, serverErrorResponseObject, { error });
  }
});

exports.refreshSeating2 = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    return authenticationRequiredResponseObject;
  }

  // Only authenticated admin can run this command
  if (!adminEmails.includes(context.auth.token.email)) {
    return authenticationRequiredResponseObject;
  }

  try {
    const mappedUsers = await getMappedUsers();

    const docRef = admin
      .firestore()
      .collection(databaseCollections.data)
      .doc(dataCollectionDocuments.users);

    await docRef.set({ mappedUsers });

    return okResponseObject;
  } catch (error) {
    logException(error);

    return Object.assign({}, serverErrorResponseObject, { error });
  }
});
