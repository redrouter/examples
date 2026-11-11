import OpenAI from "openai";

const apiKey = process.env.REDROUTER_API_KEY;
if (!apiKey) throw new Error("Set REDROUTER_API_KEY first");

const client = new OpenAI({
  apiKey,
  baseURL: "https://redrouter.org/v1",
  timeout: 120_000,
  maxRetries: 0,
});
const response = await client.chat.completions.create({
  model: "glm-5.3-flash-red",
  max_tokens: 256,
  messages: [{ role: "user", content: "Give three access-control checks for my own API." }],
});
console.log(response.choices[0]?.message.content);
