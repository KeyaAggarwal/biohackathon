// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ForensicAnchor
 * @notice Stores cryptographic anchors of synthesizer log chains on Ethereum L2
 * @dev Implements S.3741 Biosecurity Modernization Act compliance for audit trails
 * 
 * Architecture:
 * - Each synthesizer submits a daily Merkle root of their synthesis events
 * - The root is cryptographically anchored on-chain with timestamp
 * - Full logs are referenced via IPFS hash (dataUrl) for off-chain storage
 * - Authority can authorize/revoke synthesizer registrations
 */

contract ForensicAnchor {
    
    /* ========== TYPES ========== */
    
    struct AnchorEntry {
        bytes32 merkleRoot;              // Merkle root of daily synthesis log
        address synthesizer;             // Wallet that submitted the root
        string hardwareId;               // TPM/Hardware identifier
        uint256 timestamp;               // Block timestamp of submission
        string dataUrl;                  // IPFS hash or URL for full logs
        bool verified;                   // Manual verification flag
    }
    
    /* ========== STATE ========== */
    
    mapping(address => AnchorEntry[]) public anchorHistory;
    mapping(address => bool) public authorizedSynthesizers;
    mapping(bytes32 => bool) public merkleRootsSubmitted;  // For quick lookups
    
    address public owner;
    uint256 public totalSubmissions;
    
    /* ========== EVENTS ========== */
    
    event MerkleRootAnchored(
        indexed address synthesizer,
        bytes32 indexed merkleRoot,
        string hardwareId,
        uint256 timestamp,
        string dataUrl
    );
    
    event SynthesizerAuthorized(address indexed synthesizer);
    event SynthesizerRevoked(address indexed synthesizer);
    event AnchorVerified(bytes32 indexed merkleRoot);
    
    /* ========== MODIFIERS ========== */
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedSynthesizers[msg.sender], "Synthesizer not authorized");
        _;
    }
    
    /* ========== CONSTRUCTOR ========== */
    
    constructor() {
        owner = msg.sender;
        totalSubmissions = 0;
    }
    
    /* ========== ADMIN FUNCTIONS ========== */
    
    /**
     * @notice Register a new synthesizer as authorized to submit anchors
     * @param synthesizer Address of the synthesizer wallet
     */
    function authorizeSynthesizer(address synthesizer) public onlyOwner {
        require(synthesizer != address(0), "Invalid address");
        authorizedSynthesizers[synthesizer] = true;
        emit SynthesizerAuthorized(synthesizer);
    }
    
    /**
     * @notice Revoke authorization for a synthesizer
     * @param synthesizer Address of the synthesizer wallet
     */
    function revokeSynthesizer(address synthesizer) public onlyOwner {
        authorizedSynthesizers[synthesizer] = false;
        emit SynthesizerRevoked(synthesizer);
    }
    
    /**
     * @notice Manually verify an anchor (for regulatory compliance)
     * @param merkleRoot Root hash to verify
     */
    function verifyAnchorManual(bytes32 merkleRoot) public onlyOwner {
        require(merkleRootsSubmitted[merkleRoot], "Root not found");
        emit AnchorVerified(merkleRoot);
    }
    
    /* ========== PUBLIC FUNCTIONS ========== */
    
    /**
     * @notice Submit a daily Merkle root anchor
     * @param merkleRoot The root hash of the day's synthesis events
     * @param hardwareId Hardware identifier (e.g., TPM serial)
     * @param dataUrl IPFS hash or URL for full log retrieval
     */
    function submitAnchor(
        bytes32 merkleRoot,
        string calldata hardwareId,
        string calldata dataUrl
    ) public onlyAuthorized {
        require(merkleRoot != bytes32(0), "Invalid merkle root");
        require(bytes(hardwareId).length > 0, "Hardware ID required");
        require(!merkleRootsSubmitted[merkleRoot], "Root already submitted");
        
        AnchorEntry memory entry = AnchorEntry({
            merkleRoot: merkleRoot,
            synthesizer: msg.sender,
            hardwareId: hardwareId,
            timestamp: block.timestamp,
            dataUrl: dataUrl,
            verified: false
        });
        
        anchorHistory[msg.sender].push(entry);
        merkleRootsSubmitted[merkleRoot] = true;
        totalSubmissions++;
        
        emit MerkleRootAnchored(
            msg.sender,
            merkleRoot,
            hardwareId,
            block.timestamp,
            dataUrl
        );
    }
    
    /* ========== VIEW FUNCTIONS ========== */
    
    /**
     * @notice Verify if a Merkle root is anchored on-chain
     * @param synthesizer Address of the synthesizer
     * @param merkleRoot Root hash to verify
     * @return True if the root is anchored for this synthesizer
     */
    function verifyAnchor(
        address synthesizer,
        bytes32 merkleRoot
    ) public view returns (bool) {
        AnchorEntry[] storage entries = anchorHistory[synthesizer];
        
        for (uint256 i = 0; i < entries.length; i++) {
            if (entries[i].merkleRoot == merkleRoot) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @notice Get the number of anchors submitted by a synthesizer
     * @param synthesizer Address of the synthesizer
     * @return Count of submitted anchors
     */
    function getAnchorCount(address synthesizer) public view returns (uint256) {
        return anchorHistory[synthesizer].length;
    }
    
    /**
     * @notice Get a specific anchor entry
     * @param synthesizer Address of the synthesizer
     * @param index Index in the anchor history
     * @return The AnchorEntry at the specified index
     */
    function getAnchor(
        address synthesizer,
        uint256 index
    ) public view returns (AnchorEntry memory) {
        require(index < anchorHistory[synthesizer].length, "Index out of bounds");
        return anchorHistory[synthesizer][index];
    }
    
    /**
     * @notice Get the latest anchor for a synthesizer
     * @param synthesizer Address of the synthesizer
     * @return The most recent AnchorEntry
     */
    function getLatestAnchor(address synthesizer) public view returns (AnchorEntry memory) {
        require(anchorHistory[synthesizer].length > 0, "No anchors found");
        uint256 lastIndex = anchorHistory[synthesizer].length - 1;
        return anchorHistory[synthesizer][lastIndex];
    }
    
    /**
     * @notice Check if a root hash has been submitted
     * @param merkleRoot Root hash to check
     * @return True if submitted
     */
    function isMerkleRootSubmitted(bytes32 merkleRoot) public view returns (bool) {
        return merkleRootsSubmitted[merkleRoot];
    }
    
    /**
     * @notice Get total submissions across all synthesizers
     * @return Total submission count
     */
    function getTotalSubmissions() public view returns (uint256) {
        return totalSubmissions;
    }
}
