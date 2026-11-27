import Queue from 'bull';

// Keep queue construction separate from the processor. Importing application
// routes must not also launch the privileged review browser in the web process.
export const triggerXSSQueue = new Queue('trigger-xss');
