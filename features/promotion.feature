 Feature: The promotions service back-end
     As a Store Owner
     I need a RESTful catalog service
     So that I can keep track of all my promotions

 Background:
    Given the following promotions
         | id | productid  | category | available | discount |
         |  1 | 495        | two      | True      | 2        |
         |  2 | 398        | three    | True      | 3        |
         |  3 | 492        | four     | True      | 4        |

 Scenario: The server is running
     When I visit the "Home Page"
     Then I should see "Promotion Demo REST API Service" in the title
     And I should not see "404 Not Found"

 Scenario: Create a Promotion
     When I visit the "Home Page"
     And I set the "productid" to "496"
     And I set the "category" to "three"
     And I press the "Create" button
     Then I should see the message "Success"

 Scenario: List all promotions
     When I visit the "Home Page"
     And I press the "Search" button
     Then I should see "495" in the results
     And I should see "398" in the results
     And I should see "492" in the results

 Scenario: List all two
     When I visit the "Home Page"
     And I set the "Category" to "two"
     And I press the "Search" button
     Then I should see "495" in the results
     And I should not see "398" in the results
     And I should not see "492" in the results

# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Id" to "1"
#     And I press the "Retrieve" button
#     Then I should see "fido" in the "Name" field
#     When I change "Name" to "Boxer"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I set the "Id" to "1"
#     And I press the "Retrieve" button
#     Then I should see "Boxer" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see "Boxer" in the results
#     Then I should not see "fido" in the results

  Scenario: Delete a Promotion
      When I visit the "Home Page"
      And I set the "productid" to "495"
      And I press the "Search" button
      Then I should see the message "Success"
      And I should see "two" in the results
      When I copy the "id" field
      And I press the "Clear" button
      And I paste the "Id" field
      When I press the "Delete" button
      And I set the "productid" to "495"
      And I press the Search button
      Then I should not see "495" in the "productid" field
      And I should not see "two" in the "Category" field
      And the "id" field should be empty
