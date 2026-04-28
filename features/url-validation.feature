Feature: URL validation
  As a user
  I want URL validation feedback
  So that I know whether a link can be downloaded

  Scenario: URL validation success shows title and allows download
    Given the media downloader app is open
    And validation response for "https://example.com/ok" is valid with title "Demo Video"
    When I enter URL "https://example.com/ok"
    Then URL status contains "Demo Video"
    And the download button is enabled

  Scenario: URL validation failure shows an error
    Given the media downloader app is open
    And validation response for "https://example.com/bad" is invalid with error "Video unavailable"
    When I enter URL "https://example.com/bad"
    Then URL status contains "Video unavailable"
