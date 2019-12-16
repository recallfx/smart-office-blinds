const fulfilmentPodCoordinates = [
  {
    x: 485,
    y: 575,
  },
  {
    x: 574,
    y: 575,
  },
  {
    x: 574,
    y: 630,
  },
  {
    x: 485,
    y: 630,
  },
];
const cataloguePodCoordinates = [
  {
    x: 580,
    y: 575,
  },
  {
    x: 677,
    y: 575,
  },
  {
    x: 677,
    y: 630,
  },
  {
    x: 580,
    y: 630,
  },
];
const managementPodCoordinates = [
  {
    x: 680,
    y: 575,
  },
  {
    x: 805,
    y: 575,
  },
  {
    x: 805,
    y: 630,
  },
  {
    x: 680,
    y: 630,
  },
];
const nextToBangputysCoordinates = [
  {
    x: 428,
    y: 528,
  },
  {
    x: 398,
    y: 496,
  },
  {
    x: 359,
    y: 516,
  },
  {
    x: 394,
    y: 564,
  },
];
const dataPodCoordinates = [
  {
    x: 268,
    y: 379,
  },
  {
    x: 310,
    y: 351,
  },
  {
    x: 390,
    y: 480,
  },
  {
    x: 355,
    y: 510,
  },
];

const isInside = (polygon, point) => {
  // ray-casting algorithm based on
  // http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html

  const x = point.x, y = point.y;

  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x, yi = polygon[i].y;
    const xj = polygon[j].x, yj = polygon[j].y;

    const intersect = ((yi > y) !== (yj > y))
      && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }

  return inside;
}

exports.detectPod = (seatCoordinates) => {
  if (isInside(fulfilmentPodCoordinates, seatCoordinates)) {
    return 'remote_10_channel1'; // Fullfilment POD
  } else if (isInside(cataloguePodCoordinates, seatCoordinates)) {
    return 'remote_10_channel2'; // Catalogue POD
  } else if (isInside(managementPodCoordinates, seatCoordinates)) {
    return 'remote_10_channel3'; // Management POD
  } else if (isInside(dataPodCoordinates, seatCoordinates)) {
    return 'remote_9_channel3'; // Data (long room, bigger part)
  } else if (isInside(nextToBangputysCoordinates, seatCoordinates)) {
    return 'remote_9_channel4'; // Next to Bangputys (long room smaller part)
  }

  return 'no_channel';
}

