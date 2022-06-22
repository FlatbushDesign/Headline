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
  await fetch('/engine/run', { method: 'POST', credentials: "same-origin" })
  location.reload()
}

const getCredentials = async (creds) => {
  const response = await fetch(`/credentials/${creds}`, {
    credentials: "same-origin"
  })
  return await response.json()
}

const getData = async () => {
  const response = await fetch('/engine/data', {
    credentials: "same-origin"
  })

  if (response.ok) {
    return await response.json()
  } else {
    return []
  }
}

const signinGoogle = async () => {
  const response = await fetch('/auth/google/authorize')
  window.location = (await response.json()).authorization_url
}

const getCurrentUser = async () => {
  const response = await fetch("/users/me", {
    credentials: "same-origin"
  })

  if (response.ok) {
    return await response.json()
  } else {
    return null
  }
}

window.onload = function () {
  const query = new URLSearchParams(location.search)
  if (query.has('state')) {
    location.search = undefined
  }
}
