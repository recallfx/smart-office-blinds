export function capitalize([firstLetter, ...rest]) {
  return [firstLetter.toLocaleUpperCase(), ...rest].join('');
}

export function hasAllowedDomain(email, allowedDomains) {
  if (!email) {
    return false
  }

  const emailSplit = email.split('@')

  if (emailSplit.length < 2) {
    return false
  }

  return allowedDomains.includes(emailSplit[1])
}
