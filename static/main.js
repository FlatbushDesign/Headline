const API_BASE_URL = ['localhost', '127.0.0.1'].includes(location.hostname)
  ? 'http://localhost:8000'
  : 'https://headline-352617.ue.r.appspot.com'

const ALL_PROVIDERS = [
  {
    id: "slack",
    name: "Slack",
    credentials: "slack"
  },
  {
    id: "google-calendar",
    name: "Google Calendar",
    credentials: "google"
  },
  {
    id: "gmail",
    name: "GMail",
    credentials: "google"
  },
]

const getLocalDateIsoString = () => {
  const date = new Date()

  if (date.getHours() < 18) {
    date.setDate(date.getDate() - 1)
  }

  return [
    date.getFullYear(),
    (date.getMonth() + 1).toString().padStart(2, '0'),
    date.getDate().toString().padStart(2, '0'),
  ].join('-')
}

const runEngine = async () => {
  await fetch(API_BASE_URL + '/engine/run', { method: 'POST', credentials: "include" })
  location.reload()
}

const getCredentials = async (creds) => {
  const response = await fetch(API_BASE_URL + `/credentials/${creds}`, {
    credentials: "include"
  })
  return await response.json()
}

const getSubscription = async (provider) => {
  const response = await fetch(API_BASE_URL + `/subscriptions/${provider}`, {
    credentials: "include"
  })
  return await response.json()
}

const disconnectProvider = async (creds) => {
  const response = await fetch(API_BASE_URL + `/credentials/${creds}`, {
    method: 'DELETE',
    credentials: "include"
  })

  location.reload()
}

const getDataToday = async () => {
  const response = await fetch(API_BASE_URL + `/engine/data?date=${getLocalDateIsoString()}`, {
    credentials: "include"
  })

  if (response.ok) {
    return await response.json()
  } else {
    return []
  }
}

const getDataHistory = async () => {
  const response = await fetch(API_BASE_URL + `/engine/data?date__lt=${getLocalDateIsoString()}`, {
    credentials: "include"
  })

  if (response.ok) {
    return await response.json()
  } else {
    return []
  }
}

const logout = async () => {
  try {
    await fetch(API_BASE_URL + '/auth/jwt/logout', {
      method: 'POST',
      credentials: "include"
    })
    location.reload()
  } catch (e) {
    console.error('Error logging out', e)
  }
}

const signinGoogle = async () => {
  const response = await fetch(API_BASE_URL + '/auth/google/authorize')
  window.location = (await response.json()).authorization_url
}

const getCurrentUser = async () => {
  const response = await fetch(API_BASE_URL + "/users/me", {
    credentials: "include"
  })

  let user = null

  if (response.ok) {
    user = await response.json()
  }

  return user
}

window.onload = function () {
  const query = new URLSearchParams(location.search)
  if (query.has('state')) {
    location.search = undefined
  }
}
