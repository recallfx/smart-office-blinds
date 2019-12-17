'use strict';const NODE_ENV = "production";

const channels = {
	remote_10_channel1: {
		label: "Fulfillment POD",
		output_pin: 5,
		action_idle: {
			angle: 1400,
			sleep: 1
		},
		action_open: {
			angle: 900,
			sleep: 3
		},
		action_close: {
			angle: 1800,
			sleep: 3
		},
		coordinates: [
			{
				x: 485,
				y: 575
			},
			{
				x: 574,
				y: 575
			},
			{
				x: 574,
				y: 630
			},
			{
				x: 485,
				y: 630
			}
		]
	},
	remote_10_channel2: {
		label: "Catalogue POD",
		output_pin: 17,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1200,
			sleep: 3
		},
		action_close: {
			angle: 2000,
			sleep: 3
		},
		coordinates: [
			{
				x: 580,
				y: 575
			},
			{
				x: 677,
				y: 575
			},
			{
				x: 677,
				y: 630
			},
			{
				x: 580,
				y: 630
			}
		]
	},
	remote_10_channel3: {
		label: "Management POD",
		output_pin: 22,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1900,
			sleep: 3
		},
		action_close: {
			angle: 900,
			sleep: 3
		},
		coordinates: [
			{
				x: 680,
				y: 575
			},
			{
				x: 805,
				y: 575
			},
			{
				x: 805,
				y: 630
			},
			{
				x: 680,
				y: 630
			}
		]
	},
	remote_10_channel4: {
		label: "Austaras",
		output_pin: 27,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1900,
			sleep: 3
		},
		action_close: {
			angle: 1100,
			sleep: 3
		},
		coordinates: [
		]
	},
	remote_9_channel1: {
		label: "Main Kitchen",
		output_pin: 6,
		action_idle: {
			angle: 1400,
			sleep: 1
		},
		action_open: {
			angle: 900,
			sleep: 3
		},
		action_close: {
			angle: 1800,
			sleep: 3
		},
		coordinates: [
		]
	},
	remote_9_channel2: {
		label: "Aitvaras and activity room",
		output_pin: 13,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1200,
			sleep: 3
		},
		action_close: {
			angle: 2000,
			sleep: 3
		},
		coordinates: [
		]
	},
	remote_9_channel3: {
		label: "Data Pod",
		output_pin: 19,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1900,
			sleep: 3
		},
		action_close: {
			angle: 900,
			sleep: 3
		},
		coordinates: [
			{
				x: 268,
				y: 379
			},
			{
				x: 310,
				y: 351
			},
			{
				x: 390,
				y: 480
			},
			{
				x: 355,
				y: 510
			}
		]
	},
	remote_9_channel4: {
		label: "Marketing Pod, Bangputys and Perkunas",
		output_pin: 26,
		action_idle: {
			angle: 1500,
			sleep: 1
		},
		action_open: {
			angle: 1900,
			sleep: 3
		},
		action_close: {
			angle: 1100,
			sleep: 3
		},
		coordinates: [
			{
				x: 428,
				y: 528
			},
			{
				x: 398,
				y: 496
			},
			{
				x: 359,
				y: 516
			},
			{
				x: 394,
				y: 564
			}
		]
	}
};
const officeSpaceAPIToken = "c438cce34d3a830af4da7a2e704273ca";
const adminEmails = [
	"marius.bieliauskas@shopify.com",
	"alina.karpelceva@shopify.com"
];
const officeSpaceUrl = "https://shopify.officespacesoftware.com";
const officeSpaceSeatsQueryUrl = "/api/1/seats?floor_id=63";
const availableApiTokens = [
	"3a081d8d4cd1ee3ef0fc617636b5634e9635fabb"
];const databaseCollections = {
  channels: 'channels',
  commands: 'commands',
  data: 'data',
};
const dataCollectionDocuments = {
  users: 'users',
};const axios = require('axios');

function isInside(polygon, point) {
  // ray-casting algorithm based on
  // http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html

  if (!polygon || (polygon && polygon.length === 0)) {
    return false;
  }

  const x = point.x,
    y = point.y;

  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x,
      yi = polygon[i].y;
    const xj = polygon[j].x,
      yj = polygon[j].y;

    const intersect =
      yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }

  return inside;
}

function resolveChannelName(seatCoordinates) {
  const entries = Object.entries(channels);

  for (let entry of entries) {
    const [channelName, channel] = entry;

    if (isInside(channel.coordinates, seatCoordinates)) {
      return channelName;
    }
  }

  return null;
}

const officeSpaceFetchOptions = {
  headers: {
    'Content-Type': 'application/json',
    authorization: `Token token="${officeSpaceAPIToken}"`,
  },
};

async function fetchOfficeSpaceSeats() {
  let result = null;

  try {
    const response = await axios(
      Object.assign({}, officeSpaceFetchOptions, {
        url: officeSpaceUrl + officeSpaceSeatsQueryUrl,
      })
    );

    if (response.data) {
      result = response.data.response;
    }
  } catch (error) {
    console.error('fetchOfficeSpaceSeats', error);
  }

  return result;
}

async function fetchOfficeSpaceOccupancy(url) {
  let result = null;

  try {
    const response = await axios(
      Object.assign({}, officeSpaceFetchOptions, { url: officeSpaceUrl + url })
    );

    if (response.data) {
      result = response.data.response;
    }
  } catch (error) {
    console.error('fetchOfficeSpaceOccupancy', error);
  }

  return result;
}

async function getMappedUsers() {
  const seats = await fetchOfficeSpaceSeats();

  if (!seats) {
    throw new Error('Could not fetch office space seats data');
  }

  const occupiedSeatsMappedOnPod = seats
    .filter(seat => seat && seat.occupancy && seat.occupancy.employee_url)
    .map(seat => ({ channelName: resolveChannelName(seat.coordinates), employeeUrl: seat.occupancy.employee_url }))
    .filter(seat => seat.channelName);

  const promises = occupiedSeatsMappedOnPod.map(async seat => {
    const employee = await fetchOfficeSpaceOccupancy(seat.employeeUrl);

    if (employee) {
      const {channelName} = seat;
      const {email} = employee;

      return { channelName, email };
    }

    return null;
  });

  const result = await Promise.all(promises);

  // Some seats have employee url, but there is no employee for that and on request we get 404. Then error is thrown and undefined is returned.
  const filteredSeats = result.filter(item => item);

  return filteredSeats;
}const functions = require('firebase-functions');
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