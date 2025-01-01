// SPDX-License-Identifier: PLM
pragma solidity ^0.8.0;

contract FlagSubmission {
    address[] public adminList; // Array to store admin addresses
    mapping(address => bool) public admins; // Mapping to track admin status

    struct Challenge {
        string id;
        string title;
        string category;
        string description;
        string flag; // Correct flag
        uint256 points; // Points for solving
        address[] solvers; // Users who solved this challenge
    }

    Challenge[] public challenges;
    mapping(address => uint256) public userPoints; // Total points for each user

    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);
    event ChallengeAdded(string id);
    event ChallengeUpdated(string id);
    event ChallengeDeleted(string id);
    event FlagSubmitted(address indexed user, string flag);
    event ChallengeSolved(address indexed user, string challengeId, uint256 points);

    // Constructor to initialize the deploying address as an admin
    constructor() {
        admins[msg.sender] = true;
        adminList.push(msg.sender);
    }

    // Modifier to restrict access to admins
    modifier onlyAdmin() {
        require(admins[msg.sender], "Only an admin can perform this action");
        _;
    }

    // Add a new admin
    function addAdmin(address newAdmin) public onlyAdmin {
        require(newAdmin != address(0), "Invalid admin address");
        require(!admins[newAdmin], "Address is already an admin");
        admins[newAdmin] = true;
        adminList.push(newAdmin); // Add to admin list
        emit AdminAdded(newAdmin);
    }

    // Remove an admin
    function removeAdmin(address admin) public onlyAdmin {
        require(admin != msg.sender, "Admins cannot remove themselves");
        require(admins[admin], "Address is not an admin");

        // Remove admin from mapping
        admins[admin] = false;

        // Remove admin from adminList (swap and pop for efficiency)
        for (uint256 i = 0; i < adminList.length; i++) {
            if (adminList[i] == admin) {
                adminList[i] = adminList[adminList.length - 1];
                adminList.pop();
                break;
            }
        }

        emit AdminRemoved(admin);
    }

    // Get list of all admins
    function getAllAdmins() public view returns (address[] memory) {
        return adminList;
    }

    // Add a new challenge
    function addChallenge(
        string memory id,
        string memory title,
        string memory category,
        string memory description,
        string memory flag,
        uint256 points
    ) public onlyAdmin {
        for (uint256 i = 0; i < challenges.length; i++) {
            require(
                keccak256(abi.encodePacked(challenges[i].id)) != keccak256(abi.encodePacked(id)),
                "Challenge with this ID already exists"
            );
        }
        address[] memory solvers; // Initialize an empty array of solvers
        challenges.push(Challenge(id, title, category, description, flag, points, solvers));
        emit ChallengeAdded(id);
    }

    // Update an existing challenge
    function updateChallenge(
        string memory id,
        string memory title,
        string memory category,
        string memory description,
        string memory flag,
        uint256 points
    ) public onlyAdmin {
        for (uint256 i = 0; i < challenges.length; i++) {
            if (keccak256(abi.encodePacked(challenges[i].id)) == keccak256(abi.encodePacked(id))) {
                challenges[i].title = title;
                challenges[i].category = category;
                challenges[i].description = description;
                challenges[i].flag = flag;
                challenges[i].points = points;
                emit ChallengeUpdated(id);
                return;
            }
        }
        revert("Challenge not found");
    }

    // Delete a challenge
    function deleteChallenge(string memory id) public onlyAdmin {
        for (uint256 i = 0; i < challenges.length; i++) {
            if (keccak256(abi.encodePacked(challenges[i].id)) == keccak256(abi.encodePacked(id))) {
                challenges[i] = challenges[challenges.length - 1];
                challenges.pop();
                emit ChallengeDeleted(id);
                return;
            }
        }
        revert("Challenge not found");
    }

    // Submit a flag for a challenge
    function submitFlag(string memory id, string memory flag) public {
        for (uint256 i = 0; i < challenges.length; i++) {
            if (keccak256(abi.encodePacked(challenges[i].id)) == keccak256(abi.encodePacked(id))) {
                require(
                    keccak256(abi.encodePacked(challenges[i].flag)) == keccak256(abi.encodePacked(flag)),
                    "Incorrect flag!"
                );

                for (uint256 j = 0; j < challenges[i].solvers.length; j++) {
                    if (challenges[i].solvers[j] == msg.sender) {
                        emit ChallengeSolved(msg.sender, challenges[i].id, 0);
                        return;
                    }
                }

                challenges[i].solvers.push(msg.sender);
                userPoints[msg.sender] += challenges[i].points;
                emit ChallengeSolved(msg.sender, challenges[i].id, challenges[i].points);
                return;
            }
        }
        revert("Challenge not found!");
    }

    // Get solvers for a specific challenge
    function getSolvers(string memory id) public view returns (address[] memory) {
        for (uint256 i = 0; i < challenges.length; i++) {
            if (keccak256(abi.encodePacked(challenges[i].id)) == keccak256(abi.encodePacked(id))) {
                return challenges[i].solvers;
            }
        }
        revert("Challenge not found");
    }

    // Get total points for a user
    function getUserPoints(address user) public view returns (uint256) {
        return userPoints[user];
    }

    // Fetch all challenges
    function getAllChallenges() public view returns (Challenge[] memory) {
        return challenges;
    }

    // Get challenge by ID
    function getChallengeById(string memory id) public view returns (
        string memory,
        string memory,
        string memory,
        string memory,
        uint256,
        address[] memory
    ) {
        for (uint256 i = 0; i < challenges.length; i++) {
            if (keccak256(abi.encodePacked(challenges[i].id)) == keccak256(abi.encodePacked(id))) {
                Challenge memory ch = challenges[i];
                return (
                    ch.id,
                    ch.title,
                    ch.category,
                    ch.description,
                    ch.points,
                    ch.solvers
                );
            }
        }
        revert("Challenge not found");
    }

    // Get all challenges solved by a user
    function getUserSolves(address user) public view returns (Challenge[] memory) {
        uint256 count = 0;

        // Count the number of challenges solved by the user
        for (uint256 i = 0; i < challenges.length; i++) {
            for (uint256 j = 0; j < challenges[i].solvers.length; j++) {
                if (challenges[i].solvers[j] == user) {
                    count++;
                    break;
                }
            }
        }

        // Create a new array for the solved challenges
        Challenge[] memory solvedChallenges = new Challenge[](count);
        uint256 index = 0;

        for (uint256 i = 0; i < challenges.length; i++) {
            for (uint256 j = 0; j < challenges[i].solvers.length; j++) {
                if (challenges[i].solvers[j] == user) {
                    solvedChallenges[index] = challenges[i];
                    index++;
                    break;
                }
            }
        }

        return solvedChallenges;
    }

    // New function: Get all participants who attempted challenges
    function getAllParticipants() public view returns (address[] memory) {
        uint256 maxParticipants = 1000; // Arbitrary large number for the temporary array
        address[] memory tempParticipants = new address[](maxParticipants); // Declare the memory array
        uint256 count = 0;

        for (uint256 i = 0; i < challenges.length; i++) {
            for (uint256 j = 0; j < challenges[i].solvers.length; j++) {
                address solver = challenges[i].solvers[j];

                // Check if the solver is already added
                bool isAdded = false;
                for (uint256 k = 0; k < count; k++) {
                    if (tempParticipants[k] == solver) {
                        isAdded = true;
                        break;
                    }
                }

                // Add the solver if not already added
                if (!isAdded) {
                    tempParticipants[count] = solver;
                    count++;
                }
            }
        }

        // Copy valid participants to a dynamically-sized array
        address[] memory participants = new address[](count);
        for (uint256 i = 0; i < count; i++) {
            participants[i] = tempParticipants[i];
        }

        return participants;
    }


}
