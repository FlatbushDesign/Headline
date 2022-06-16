const currentUser = "62a9e25492b9284956ea2fe8"
const authHeader = { Authorization: 'Bearer fake-token' }

const ALL_PROVIDERS = [
  {
    id: "slack",
    name: "Slack"
  },
  {
    id: "google-calendar",
    name: "Google Calendar"
  },
  {
    id: "gmail",
    name: "GMail"
  },
  {
    id: "zoom",
    name: "Zoom"
  }
]

const runEngine = async () => {
  fetch('/engine/run', { method: 'POST', headers: { ...authHeader } })
}

const getCredentials = async (creds) => {
  const response = await fetch(`/credentials/${creds}`, { headers: { ...authHeader } })
  return await response.json()
}

const getData = async () => {
  const response = await fetch('/engine/data', { method: 'GET', headers: { ...authHeader } })
  return await response.json()
}
