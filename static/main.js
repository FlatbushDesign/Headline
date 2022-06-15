const currentUser = "62a9e25492b9284956ea2fe8"

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
  fetch('/engine/run', { method: 'POST' })
}

const getCredentials = async (creds) => {
  const response = await fetch(`/credentials/${creds}`, { headers: { Authorization: 'Bearer stocazzo' } })
  return await response.json()
}

