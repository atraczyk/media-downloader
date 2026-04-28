Feature: Download lifecycle
  As a user
  I want clear progress and controls during downloads
  So that I can monitor, cancel, and open results

  Scenario: Progress, completion, and Show in folder are wired
    Given the media downloader app is open
    And validation response for "https://example.com/audio" is valid with title "Audio File"
    And start download succeeds
    When I enter URL "https://example.com/audio"
    And I start the download
    And download reports status "downloading" progress 0.5 message "Downloading chunk"
    Then progress message contains "Downloading chunk"
    When download completes successfully with file "C:\Downloads\Audio File.mp3"
    Then Show in folder action is available
    When I click Show in folder
    Then shell show item is called with "C:\Downloads\Audio File.mp3"

  Scenario: Active download can be canceled
    Given the media downloader app is open
    And validation response for "https://example.com/cancel" is valid with title "Cancelable"
    And start download succeeds
    When I enter URL "https://example.com/cancel"
    And I start the download
    Then cancel button is shown
    When I cancel the download
    Then cancel download was requested 1 time
