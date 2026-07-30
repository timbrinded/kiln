export function isFeatureEnabled(config) {
  let enabled = false;

  if (config.enabled === true) {
    enabled = true;
  } else {
    enabled = false;
  }

  return enabled;
}
