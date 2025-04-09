export default async function fetchData(api, info) {
    const headers = { 'Content-Type': 'application/json' }

    const options = {
      method: 'POST',
      body: info ? info : JSON.stringify(),
    };
    
    if (!info) {
      options.headers = headers;
    }
    
    const res = await fetch(api, options);

    const data = await res.json()
    
    if (data.errors) {
      console.error(data.errors)
      throw new Error('Failed to fetch API')
    }
    return data
}