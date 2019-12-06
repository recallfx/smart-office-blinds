export function capitalize([firstLetter, ...rest]) {
    return [firstLetter.toLocaleUpperCase(), ...rest].join('')
  }
  