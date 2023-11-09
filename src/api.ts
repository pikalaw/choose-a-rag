export async function getWelcome(): Promise<string> {
  const response = await fetch('http://localhost:8001/');
  const message = await response.json();
  return message.message;
}
