// Prod:
// const API_BASE_URL = 'https://headline-352617.ue.r.appspot.com'
// Dev:
const API_BASE_URL = 'http://localhost:8000'

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
  {
    id: "zoom",
    name: "Zoom",
    credentials: "zoom"
  }
]

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

const getData = async () => {
  const response = await fetch(API_BASE_URL + '/engine/data', {
    credentials: "include"
  })

  if (response.ok) {
    return await response.json()
  } else {
    return []
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
