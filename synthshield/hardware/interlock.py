# Solenoid Valve Control Simulation
# This module implements the firmware-level handshake for solenoid valve control.

import hmac
import hashlib
import base64
import json
import time

class SolenoidValveController:
    def __init__(self, root_of_trust_key=b"root_of_trust_secret"):
        self.valves = {"valve_1": False, "valve_2": False}  # All valves de-energized by default
        self.root_of_trust_key = root_of_trust_key
        self.status = "LOCKED"

    def _decode_permission_token(self, permission_token):
        """
        Parse token format: v1.<base64url_payload_json>.<signature_hex>
        """
        parts = permission_token.split(".")
        if len(parts) != 3 or parts[0] != "v1":
            return None, None, False
        payload_b64, signature = parts[1], parts[2]
        try:
            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_json.decode("utf-8"))
        except Exception:
            return None, None, False
        return payload, payload_json, True

    def authorize(self, permission_token, expected_sequence_hash=None, expected_chunk_bp=100):
        # Verify signed permission token emitted by Sentinel module
        if not permission_token:
            return False

        payload, payload_json, parsed = self._decode_permission_token(permission_token)
        if not parsed:
            return False

        provided_sig = permission_token.split(".")[2]
        expected_sig = hmac.new(
            self.root_of_trust_key,
            payload_json,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(provided_sig, expected_sig):
            return False

        now_ts = int(time.time())
        if payload.get("exp", 0) < now_ts:
            return False

        if expected_sequence_hash and payload.get("sequence_hash") != expected_sequence_hash:
            return False

        if expected_chunk_bp is not None and payload.get("chunk_bp") != expected_chunk_bp:
            return False

        return True

    def actuate_valve(self, valve_id, permission_token, expected_sequence_hash=None, expected_chunk_bp=100):
        if valve_id not in self.valves:
            raise ValueError(f"Invalid valve ID: {valve_id}")

        if self.authorize(
            permission_token,
            expected_sequence_hash=expected_sequence_hash,
            expected_chunk_bp=expected_chunk_bp
        ):
            self.valves[valve_id] = True  # Energize the valve
            self.status = "AUTHORIZED"
            print(f"Valve {valve_id} actuated. Status: {self.status}")
            return True
        else:
            self.status = "LOCKED"
            print("Authorization failed. Valve remains closed.")
            return False

    def reset_valves(self):
        for valve in self.valves:
            self.valves[valve] = False  # De-energize all valves
        print("All valves reset to default state.")

# Example usage
if __name__ == "__main__":
    controller = SolenoidValveController()
    
    # Try with invalid token
    valid_token = "v1.invalid.payload"
    controller.actuate_valve("valve_1", valid_token)
    
    controller.reset_valves()