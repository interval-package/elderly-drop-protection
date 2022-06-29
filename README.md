# elderly-drop-protection

Emergencies can happen suddenly and without warning. That is why fall detection technology is an invaluable, life-saving feature in medical alert systems. If you can't press the help button after a fall or during a medical emergency, the automatic fall detection feature of a medical alert system can give you the peace of mind that you will still receive the help that you need.

## Detecting falls

Fall detection devices automatically employ the technology to detect and get fast assistance for a senior that is prone to falls. A fall detection medical alert system allows the user to summon help without having to press the call button. These systems automatically activate the sensor if the user suffers a fall. The built-in technology can be worn around the neck or, depending on the device, on your wrist or on your waist.

## How does fall detection work?

**Sensors.** Fall detection systems use accelerometers, a type of low power radio wave technology sensor, to monitor the movements of the user. State-of-the-art fall detection devices use three axis accelerometers, like those that are used within smartwatches and [smartphones](https://www.lively.com/phones/lively-smart/). Some fall detection devices use a built-in tri-axial accelerometer with patented algorithms developed by BioSensics.

**Fall detection.** The fall alert detectors can measure when the user has suddenly fallen by detecting the abrupt changes of body movements. The technology can evaluate an individual’s body position, physical activity, and the smoothness of acceleration of movements, says the [International Journal of Telemedicine and Applications](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4346101/). If the device determines that these variables are within the danger zone and a fall has occurred, it will automatically activate an emergency fall alert and call emergency response agents for assistance.

Fall detection has become an important stepping stone in the research of action recognition — which is to train an AI to classify general actions such as walking and sitting down. What humans interpret as an obvious action of a person falling face flat is but a sequence of jumbled up pixels for an AI. To enable the AI to make sense of the input it receives, we need to teach it to detect certain patterns and shapes, and formulate its own rules.

To build an AI to detect falls, I decided not to go through the torture of amassing a large dataset and training a model specifically for this purpose. Instead, I used pose estimation as the building block.

