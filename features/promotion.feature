 Feature: The promotions service back-end
     As a Store Owner
     I need a RESTful catalog service
     So that I can keep track of all my promotions

 Background:
    Given the following promotions
         | productid  | category | available | discount |
         | 495        | two      | true      |    2     |
         | 398        | three    | true      |    3     |
         | 492        | four     | true      |    4     |

 Scenario: The server is running
     When I visit the "Home Page"
     Then I should see "Promotion Demo REST API Service" in the title
     And I should not see "404 Not Found"

 Scenario: Create a Promotion
     When I visit the "Home Page"
     And I set the "productid" to "496"
     And I set the "category" to "three"
     And I set the "discount" to "5"
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

 Scenario: Update a Promotion
     When I visit the "Home Page"
     And I set the "productid" to "495"
     And I press the "Search" button
     Then I should see "495" in the "productid" field
     And I should see "two" in the "Category" field
     When I change "productid" to "300"
     And I press the "Update" button
     Then I should see the message "Success"
     When I copy the "Id" field
     And I press the "Clear" button
     And I paste the "Id" field
     And I press the "Retrieve" button
     Then I should see "300" in the "productid" field
     When I press the "Clear" button
     And I press the "Search" button
     Then I should see "300" in the results
     And I should not see "495" in the results

Scenario: Cancel a Promotion
     When I visit the "Home Page"
     And I set the "productid" to "398"
     And I press the "Search" button
     Then I should see "398" in the "productid" field
     And I should see "three" in the "Category" field
     When I copy the "Id" field
     And I press the "Clear" button
     And I paste the "Id" field
     And I press the "Cancel" button
     Then I should see the message "Success"
     When I copy the "Id" field
     And I press the "Clear" button
     And I paste the "Id" field
     And I press the "Retrieve" button
     Then I should see "false" in the "available" field

 Scenario: Retrieve a Promotion
     When I visit the "Home Page"
     And I set the "productid" to "495"
     And I press the "Search" button
     When I copy the "Id" field
     And I press the "Clear" button
     And I paste the "Id" field
     And I press the "Retrieve" button
     Then I should see "495" in the "productid" field
#     And I should see "two" in the "Category" field
#     And I should see "2" in the "discount" field

Scenario: Delete a Promotion
      When I visit the "Home Page"
      And I set the "productid" to "492"
      And I press the "Search" button
      Then I should see "492" in the "productid" field
      And I should see "four" in the "Category" field
      When I copy the "Id" field
      And I press the "Clear" button
      And I paste the "Id" field
      And I press the "Delete" button
      When I visit the "Home Page"
      And I press the "Search" button
      Then I should see "495" in the results
      And I should see "398" in the results
      And I should not see "492" in the results
