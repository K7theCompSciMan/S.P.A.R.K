import jwt from "jsonwebtoken";
import { configDotenv } from "dotenv";
configDotenv();
export const signJwt = (
  payload: Object,
  keyName: "accessTokenPrivateKey" | "refreshTokenPrivateKey",
  options?: jwt.SignOptions | undefined
): string => {
  try {
    const key = Buffer.from(getEnv(keyName), "base64").toString("ascii");
    return jwt.sign(payload, key, {
      ...(options && options),
      algorithm: "RS256",
    });
  } catch (err) {
    
    return "Error signing JWT";
  }
};

export function verifyJwt<T>(
  token: string,
  keyName: "accessTokenPublicKey" | "refreshTokenPublicKey"
): T | null {
  // log.info(`Verifying JWT for token ${token}`);
  const publicKey = Buffer.from(getEnv(keyName), "base64").toString("ascii");
  // log.info(`Got key ${publicKey}`);
  try {
    const decoded = jwt.verify(token, publicKey) as T;
    return decoded;
  } catch (err) {
    return null;
  }
}

function getEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Environment variable ${key} not set`);
  }
  return value;
}
