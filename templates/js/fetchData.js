export default async function fetchData(api) {
    const headers = { 'Content-Type': 'application/json' }

    const res = await fetch(api, {
      headers,
      method: 'POST',
      body: JSON.stringify(),
    })

    const data = await res.json()
    
    if (data.errors) {
      console.error(data.errors)
      throw new Error('Failed to fetch API')
    }
    return data
}