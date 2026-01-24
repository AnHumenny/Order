interface Token {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string): Promise<Token> {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const response = await fetch(`${import.meta.env.VITE_API_URL}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  return data;
}
