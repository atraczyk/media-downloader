Feature: Transcript panel
  As a user
  I want transcript data displayed when available
  So that I can review captions in-app

  Scenario: Transcript panel can be shown when transcript text arrives
    Given the media downloader app is open
    When transcript text arrives "Hello transcript"
    Then transcript section is visible
    When I click transcript toggle
    Then transcript text contains "Hello transcript"
