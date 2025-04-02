#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
RESET='\033[0m'

# Function for animated text
animate_text() {
  local text="$1"
  local speed="${2:-0.03}"  # Default speed is 0.03 seconds per character
  
  # Print text from left to right
  printf "${CYAN}"
  for ((i=1; i<=${#text}; i++)); do
    printf "%s" "${text:0:i}"
    printf "\r"
    sleep $speed
  done
  printf "${RESET}\n"
  
  # Short pause at the end
  sleep 0.2
}

# Function to show fancy progress
show_fancy_progress() {
    local progress=$1
    local total=$2
    local percentage=$((100*progress/total))
    local bar_size=30
    local filled_size=$((percentage*bar_size/100))
    
    # Print the progress percentage
    printf "\r[" 
    
    # Create the progress bar with gradient colors
    for ((i=0; i<bar_size; i++)); do
        if [ $i -lt $filled_size ]; then
            if [ $i -lt $((bar_size/3)) ]; then
                printf "${RED}#${RESET}"
            elif [ $i -lt $((bar_size*2/3)) ]; then
                printf "${YELLOW}#${RESET}"
            else
                printf "${GREEN}#${RESET}"
            fi
        else
            printf "${WHITE}-${RESET}"
        fi
    done
    
    # Print the percentage
    printf "] %3d%%" "$percentage"
}

# Function to print a banner
print_banner() {
    clear
    echo -e "${PURPLE}=======================================${RESET}"
    echo -e "${PURPLE}     X M R i g   M i n e r   S e t u p ${RESET}"
    echo -e "${PURPLE}=======================================${RESET}"
    echo -e "${YELLOW}     Automated Installation Script     ${RESET}"
    echo -e "${PURPLE}=======================================${RESET}"
    echo ""
}

# Function to install Ubuntu in Termux
install_ubuntu() {
    print_banner
    
    echo -e "${YELLOW}[*] Installing Ubuntu in Termux...${RESET}"
    echo ""
    
    # Variables for progress tracking
    total_steps=4
    current_step=0
    
    # Step 1: Update packages
    animate_text "Updating packages..."
    pkg update -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 2: Install required packages
    animate_text "Installing required packages..."
    pkg install wget curl proot tar -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 3: Download Ubuntu installer
    animate_text "Downloading Ubuntu installer..."
    wget https://raw.githubusercontent.com/AndronixApp/AndronixOrigin/master/Installer/Ubuntu20/ubuntu20.sh -O ubuntu20.sh -q
    chmod +x ubuntu20.sh
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 4: Run Ubuntu installer (selecting default options)
    animate_text "Running Ubuntu installer (this might take a while)..."
    # Run the script and automatically select default options
    yes "" | bash ubuntu20.sh > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    echo ""
    echo -e "${GREEN}✅ Ubuntu installation completed successfully!${RESET}"
    echo -e "${YELLOW}[*] You can now start Ubuntu by running ./start-ubuntu.sh${RESET}"
    echo ""
}

# Create run.sh script for easy restart
create_restart_script() {
    local install_dir=$(pwd)
    
    cat > run.sh << EOF
#!/bin/bash
cd $(pwd)
./xmrig
EOF
    
    chmod +x run.sh
    echo -e "${GREEN}Created restart script: run.sh${RESET}"
}

# Main installation function
install_miner() {
    print_banner
    
    echo -e "${YELLOW}[*] This script will automatically set up XMRig cryptocurrency miner${RESET}"
    echo -e "${YELLOW}[*] Installation progress:${RESET}"
    echo ""
    
    # Variables for progress tracking
    total_steps=12
    current_step=0
    
    # Step 1: Install wget
    animate_text "Installing wget..."
    apt install wget -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 2: Install proot
    animate_text "Installing proot..."
    apt install proot -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 3: Install git
    animate_text "Installing git..."
    apt install git -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 4: Install nano
    animate_text "Installing nano..."
    apt install nano -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 5: Install zip
    animate_text "Installing zip..."
    apt install zip -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 6: Install development packages
    animate_text "Installing development packages..."
    apt install git build-essential cmake libuv1-dev libmicrohttpd-dev libssl-dev -y > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 7: Download XMRig
    animate_text "Downloading XMRig..."
    wget https://github.com/dikripto/xmrig/archive/refs/heads/master.zip -q
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 8: Unzip XMRig
    animate_text "Extracting XMRig..."
    unzip -q master.zip
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 9: Create build directory and enter
    animate_text "Creating build directory..."
    cd xmrig-master
    mkdir -p build
    cd build
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 10: Configure with CMake
    animate_text "Running CMake configuration..."
    cmake .. -DWITH_HWLOC=OFF > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 11: Compile with Make
    animate_text "Compiling XMRig (this may take a while)..."
    make -j$(nproc) > /dev/null 2>&1
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Step 12: Download config file
    animate_text "Downloading configuration file..."
    wget https://gist.githubusercontent.com/dytra/5b17acdd38fcabba83e6411f38cce5ad/raw/9214159292a479ec5c27ac7ea28d0da00ca99d4f/config.json -q
    current_step=$((current_step+1))
    show_fancy_progress $current_step $total_steps
    echo -e " ${GREEN}✓${RESET}"
    
    # Create restart script
    create_restart_script
    
    # Setup mining configuration
    echo ""
    echo -e "${BLUE}=======================================${RESET}"
    echo -e "${BLUE}     ${WHITE}MINER CONFIGURATION SETUP${BLUE}     ${RESET}"
    echo -e "${BLUE}=======================================${RESET}"
    echo ""
    
    # Ask for wallet address
    echo -e "${YELLOW}[?] Please enter your wallet address:${RESET}"
    read -p "> " wallet_address
    
    # Ask for worker name
    echo -e "${YELLOW}[?] Please enter your worker name:${RESET}"
    read -p "> " worker_name
    
    # Update the config.json file with the user's wallet and worker name
    sed -i "s/D5wNKhb3fgnyk6NPEFtrgYta5YaSMg38pP/$wallet_address/g" config.json
    sed -i "s/worker1/$worker_name/g" config.json
    
    # Display summary
    echo ""
    echo -e "${GREEN}✅ Installation completed successfully!${RESET}"
    echo ""
    echo -e "${CYAN}=======================================${RESET}"
    echo -e "${CYAN}        MINING CONFIGURATION          ${RESET}"
    echo -e "${CYAN}=======================================${RESET}"
    echo -e "${WHITE}Wallet address: ${YELLOW}$wallet_address${RESET}"
    echo -e "${WHITE}Worker name:    ${YELLOW}$worker_name${RESET}"
    echo -e "${CYAN}=======================================${RESET}"
    echo ""
    
    # Countdown to mining
    echo -e "${YELLOW}[*] Mining will start in:${RESET}"
    for i in {5..1}; do
        echo -ne "${RED}$i...${RESET}"
        sleep 1
    done
    echo -e "${GREEN}START!${RESET}"
    echo ""
    
    # Create run.sh script in the main directory
    cd ../../
    cat > run.sh << EOF
#!/bin/bash
# Automatically restart XMRig mining
cd "$(pwd)/xmrig-master/build"
./xmrig
EOF
    chmod +x run.sh
    
    # Start the miner
    cd xmrig-master/build
    ./xmrig
}

# Main script execution
print_banner

# Ask if the user wants to install Ubuntu
echo -e "${YELLOW}[?] Would you like to install Ubuntu in Termux? (y/n)${RESET}"
read -p "> " install_ubuntu_choice

# Process the user's choice
if [[ "$install_ubuntu_choice" =~ ^[Yy]$ ]]; then
    # User chose to install Ubuntu
    install_ubuntu
    
    # Ask the user if they want to enter Ubuntu and continue with miner installation
    echo -e "${YELLOW}[?] Would you like to enter Ubuntu and install the XMRig miner now? (y/n)${RESET}"
    read -p "> " enter_ubuntu_choice
    
    if [[ "$enter_ubuntu_choice" =~ ^[Yy]$ ]]; then
        # Start Ubuntu and run the XMRig installation
        echo -e "${GREEN}[*] Starting Ubuntu and installing XMRig...${RESET}"
        echo ""
        
        # Copy this script to Ubuntu
        cp "$0" ubuntu-fs/root/setup.sh
        chmod +x ubuntu-fs/root/setup.sh
        
        # Enter Ubuntu and run the setup script with a flag to skip Ubuntu installation
        ./start-ubuntu.sh bash -c "cd ~ && bash setup.sh --skip-ubuntu"
        exit 0
    else
        echo -e "${YELLOW}[*] You can enter Ubuntu later by running ./start-ubuntu.sh${RESET}"
        echo -e "${YELLOW}[*] Then run this script again inside Ubuntu${RESET}"
        exit 0
    fi
else
    # Check if script is running with --skip-ubuntu flag (inside Ubuntu)
    if [[ "$1" == "--skip-ubuntu" ]]; then
        # Skip Ubuntu installation and proceed with miner installation
        install_miner
    else
        # Running in Termux but chose not to install Ubuntu
        echo -e "${YELLOW}[*] Proceeding with XMRig installation directly in Termux...${RESET}"
        echo ""
        
        install_miner
    fi
fi