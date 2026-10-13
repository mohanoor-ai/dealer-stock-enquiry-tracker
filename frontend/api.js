// All browser-to-backend calls live here.
export async function request(path, method = 'GET', data) {
  const options = {method, headers:{'Content-Type':'application/json'}};
  if (data !== undefined) options.body = JSON.stringify(data);
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : `Check your input (${response.status})`);
  return result;
}
export function poundsToPence(value) {
  if (!/^\d+(\.\d{1,2})?$/.test(String(value))) throw new Error('Enter pounds with up to two decimal places');
  const [pounds, decimal=''] = String(value).split('.');
  const result = Number(pounds)*100 + Number(decimal.padEnd(2,'0'));
  if (!Number.isSafeInteger(result) || result > 100000000) throw new Error('Price is too large');
  return result;
}
export function money(pence) {return new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(pence/100);}
