import {
  channels,
  officeSpaceAPIToken,
  officeSpaceUrl,
  officeSpaceSeatsQueryUrl,
} from '../../config.json';

const axios = require('axios');

export function isInside(polygon, point) {
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

export function resolveChannelName(seatCoordinates) {
  const entries = Object.entries(channels);

  for (let entry of entries) {
    const [channelName, channel] = entry;

    if (isInside(channel.coordinates, seatCoordinates)) {
      return channelName;
    }
  }

  return null;
}

export const officeSpaceFetchOptions = {
  headers: {
    'Content-Type': 'application/json',
    authorization: `Token token="${officeSpaceAPIToken}"`,
  },
};

export async function fetchOfficeSpaceSeats() {
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

export async function fetchOfficeSpaceOccupancy(url) {
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

export default async function getMappedUsers() {
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
}
