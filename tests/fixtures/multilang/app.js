import { Helper } from "./helper.js";

export function greet(name) {
  return `hi ${name}`;
}

export class Widget {
  render() { return "<div>"; }
  destroy() { return true; }
}
