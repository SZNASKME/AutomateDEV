import json
from utils.pathHolder import FEATURES_JSON_PATH


class FeatureManager:
    def __init__(self):
        self.features = self.loadFeatures()

    def loadFeatures(self):
        """Loads the features from the JSON file."""
        try:
            with open(FEATURES_JSON_PATH, 'r') as f:
                data = json.load(f)
                return data.get('features', [])
        except FileNotFoundError:
            print("Features JSON file not found. Creating a default one.")
            # Default features if the file is missing
            return []
    
    def updateFeature(self, feature_name, enabled):
        """Enable or disable a feature and update the JSON file."""
        for feature in self.features:
            if feature['name'] == feature_name:
                feature['enabled'] = enabled
                self.save_features()
                print(f"Feature '{feature_name}' updated to {'enabled' if enabled else 'disabled'}.")
                break
    
    def saveFeatures(self):
        """Saves the updated features list to the JSON file."""
        with open(FEATURES_JSON_PATH, 'w') as f:
            json.dump({"features": self.features}, f, indent=4)
    
    def listEnabledFeatures(self):
        """Lists all enabled features."""
        enabled = [feature for feature in self.features if feature['enabled']]
        return enabled
    
    def getFeatureInputs(self, feature_name):
        """Get the input fields for a specific feature."""
        for feature in self.features:
            if feature['name'] == feature_name:
                return feature.get('inputs', [])
        return []