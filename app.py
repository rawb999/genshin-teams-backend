from flask import Flask, jsonify, request
from flask_cors import CORS
from copy import deepcopy
from character_data import characters_info_original


def find_team(main_character, owned_characters_original, selected_team_type):
    owned_characters = owned_characters_original
    characters_info = deepcopy(characters_info_original)
    owned_characters.remove(main_character)
    team = [main_character]  # Start with the main character in the team
    team_specs = (
        characters_info.get(main_character)
        .get("team_types", {})
        .get(selected_team_type, {})
    )  # dictionary with team data
    required_elements = team_specs.get("required_elements", [])
    required_roles = team_specs.get("required_roles", [])
    character_groups = team_specs.get("character_groups", {})
    character_groups_amounts = team_specs.get("character_groups_amounts", {})
    specific_combo = team_specs.get("specific_combo", {})

    group_counts = {group_name: 0 for group_name in character_groups}
    recommended_characters = team_specs.get("recommended_teammates", [])
    owned_characters = sorted(owned_characters, key=lambda x: characters_info[x]["rank"]) #sort based on rank lower # is higher rank
    recommended_characters = sorted(recommended_characters, key=lambda x: characters_info[x]["rank"])
    mandatory_characters = team_specs.get("mandatory", [])
    removed_characters = []


    if len(characters_info[team[0]]['role']) == 1 and characters_info[team[0]]['role'][0] == 'on-field':
                print('called')
                for x in owned_characters:
                    if len(characters_info[x]['role']) == 1 and characters_info[x]['role'][0] == 'on-field':
                        print('removed ' + x)
                        removed_characters.append(x)
                        owned_characters.remove(x)
                        


    # if there is a specific combo of role + element required, look for characters that satisfy this
    def combos(candidate):
        char_info = characters_info[candidate]
        for required_element, required_role in specific_combo.items():
            if char_info["element"] == required_element and any(
                role in char_info["role"] for role in required_role
            ):
                add_if_fits_requirements(candidate, True, True)
                return True
        return False

    def is_group_limit_reached(candidate):
        for group_name, members in character_groups.items():
            if candidate in members:
                if group_counts[group_name] >= character_groups_amounts[group_name]:
                    return True
        return False
    
    def group_limit_add(added):
        for group_name, members in character_groups.items():
            if added in members: 
                group_counts[group_name] += 1
                return True
        return False


    # AT SOME POINT SORT THE OWNED CHARACTERS LISTS AND RECOMMENDED CHARACTERS LIST BY A TIER LIST ORDER BEFORE SORT
    # AT SOME POINT MAKE IT SO IF IT DOESN'T GET ALL OF THE CHARACTERS TO BE PROPERLY ON-ELEMENT AND ON-ROLE, IT NOTIFIES THE USER THEY DONT HAVE THE NECESSARY CHARACTERS
    # AT SOME POINT ADD THE OPTION TO REMOVE A CHARACTER FROM THE CREATED TEAM AND REMAKE ANOTHER VARIATION
    # Helper function to check and add a character if they fit the requirements
    # check_elements will be passed as true or false depending on whether we're considering the elements or roles in the decision
    def add_if_fits_requirements(char_name, check_elements=True, check_roles=True):
        if is_group_limit_reached(char_name):
            return False
        if len(team) >= 4:  # check to see if team is full
            return False
        char_info = characters_info[
            char_name
        ]  # character being evaluated for fit on team
        fits_element = False
        fits_role = False
        if check_roles:
            if (
                (4 - len(team)) > len(required_roles)
            ):  # indicates there is 1 or more flex slots on the team so no mandatory role to fill
                fits_role = True
            for x in char_info[
                "role"
            ]:  # iterate through all the possible roles for that character
                for y in required_roles:
                    if x in y:
                        fits_role = True
        else:
            fits_role = True
        if check_elements:
            if (4 - len(team)) > len(required_elements):
                fits_element = True
            for x in required_elements:
                if char_info["element"] in x:
                    fits_element = True
        else:
            fits_element = True

        if fits_role and fits_element:
            team.append(char_name)
            group_limit_add(char_name)
            removedRole = False
            removedElement = False

            while removedRole is False and required_roles:
                for x in required_roles:  # check each value in character roles
                    for y in char_info["role"]: # iterate over every list inside required_roles
                        if y in x:  # the role is in that list
                            required_roles.remove(
                                x
                            )  # remove the whole list because that slot is filled
                            print(required_roles)
                            removedRole = True
                            break
                    if removedRole:
                        break
                if not removedRole:
                    break
            while removedElement is False and required_elements:
                for x in required_elements:
                    if char_info["element"] in x:
                        required_elements.remove(x)
                        removedElement = True
                        break
                if not removedElement:
                    break
            owned_characters.remove(char_name)
            if len(char_info['role']) == 1 and char_info['role'][0] == 'on-field':
                for x in owned_characters:
                    if len(characters_info[x]['role']) == 1 and characters_info[x]['role'][0] == 'on-field':
                        removed_characters.append(x)
                        owned_characters.remove(x)

            print("added: " + char_name)
            return True
        return False
    
    if 'nilou' in owned_characters:
        nilou_element_count = 0
        for x in required_elements:
            if 'hydro' in x or 'dendro' in x:
                nilou_element_count += 1
        if nilou_element_count < 3:
            removed_characters.append('nilou')
            owned_characters.remove('nilou')
            
    
    if 'chevreuse' in owned_characters:
        chevreuse_element_count = 0
        for x in required_elements:
            if 'pyro'in x or 'electro' in x:
                chevreuse_element_count += 1
        if chevreuse_element_count < 3:
            removed_characters.append('chevreuse')  
            owned_characters.remove('chevreuse')
            
    
    for mandatory in mandatory_characters:
         if mandatory in owned_characters:
              add_if_fits_requirements(mandatory, check_elements = False, check_roles = False)
    
    for recommended in recommended_characters:
        if recommended in owned_characters and recommended not in team:
            combos(recommended)

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team

    for non_recommended in owned_characters:
        if non_recommended not in team:
            combos(non_recommended)

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team

    # 1. add recommended teammates with correct element and role
    print("reached rec + ele + role")
    for recommended in recommended_characters:
        if recommended in owned_characters and recommended not in team:
            add_if_fits_requirements(recommended, check_elements=True, check_roles=True)

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team

    # 2. add non_recommended characters that fit element and role
    print("reached non-rec + ele + role")
    for non_recommended in owned_characters:
        if non_recommended not in team:
            add_if_fits_requirements(
                non_recommended, check_elements=True, check_roles=True
            )

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team

    # 3. add recommended teammates with correct element but not role
    # only check if elements list not empty
    print("reached rec + ele")
    if len(required_elements) > 0:
        for recommended in recommended_characters:
            if recommended in owned_characters and recommended not in team:
                add_if_fits_requirements(
                    recommended, check_elements=True, check_roles=False
                )
    
    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team


    # 4. add non_recommended teammates with correct element but not role
    print("reached non-rec + ele")
    if len(required_elements) > 0:
        for non_recommended in owned_characters:
            if non_recommended not in team:
                add_if_fits_requirements(
                    non_recommended, check_elements=True, check_roles=False
                )

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team
    
    # 5. add recommended teammates with correct role but wrong element
    print("reached rec + role")
    if len(required_roles) > 0:
        for recommended in recommended_characters:
            if recommended in owned_characters and recommended not in team:
                add_if_fits_requirements(
                    recommended, check_elements=False, check_roles=True
                )

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team
    
    # 6. add non_recommended characters with correct role but wrong element
    print("reached non-rec + role")
    if len(required_roles) > 0:
        for non_recommended in owned_characters:
            if non_recommended not in team:
                add_if_fits_requirements(
                    non_recommended, check_elements=False, check_roles=True
                )
    
    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team
    
    for x in removed_characters:
         owned_characters.append(x)

    # 7. add recommended characters regardless if satisfying criteria
    print("reached rec")
    for recommended in owned_characters:
        if recommended in owned_characters and recommended not in team:
            add_if_fits_requirements(
                recommended, check_elements=False, check_roles=False
            )

    if len(team) >= 4: 
            print('Done. Team: ')
            print(team)
            return team
    
    # 8. add from a list of generally good characters

    # 9. add random characters if team not full
    print("reached random")
    for char_name in owned_characters:
        if len(team) >= 4:
            break
        if char_name not in team:
            team.append(char_name)
    return team


# when storing elements for a team, always put the multi-option slots first
# role": ["on-field", "off-field", "def", "heal", "buff", "battery", "group", "bloomActivator", "plungeAttacker", "shield"]
# character groups and the amounts are for if the guide recommends a 1 or 2 etc from a group of possible recommended characters
# only one character is needed for hydro app, add a dict entry of xignqiu: yelan and vice versa

app = Flask(__name__)

CORS(app)


@app.route("/submit-characters", methods=["POST"])
def submit_characters():
    data = request.json
    selected_characters = data.get("selectedCharacters", [])
    primary_character = data.get("primaryCharacter", [])
    selected_team = data.get("selectedTeamType")
    print("Selected Characters:", selected_characters)
    print("Primary Character:", primary_character)
    print("Selected Team:", selected_team)

    return find_team(primary_character, selected_characters, selected_team)


if __name__ == "__main__":
    app.run(debug=True)


def test():
    main_character = "gaming"
    selected_team_type = "vape"
    owned_characters = {"bennett", "ayaka", "xiangling"}
    team = find_team(main_character, owned_characters, selected_team_type)
    print(team)
