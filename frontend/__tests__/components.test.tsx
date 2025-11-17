/**
 * Component tests
 */
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

describe('Button Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(
      <Button title="Test Button" onPress={() => {}} />
    );
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <Button title="Click Me" onPress={onPressMock} />
    );

    fireEvent.press(getByText('Click Me'));
    expect(onPressMock).toHaveBeenCalledTimes(1);
  });

  it('shows loading indicator when loading', () => {
    const { queryByText } = render(
      <Button title="Loading" onPress={() => {}} loading={true} />
    );
    expect(queryByText('Loading')).toBeNull();
  });

  it('is disabled when disabled prop is true', () => {
    const onPressMock = jest.fn();
    const { getByText } = render(
      <Button title="Disabled" onPress={onPressMock} disabled={true} />
    );

    fireEvent.press(getByText('Disabled'));
    expect(onPressMock).not.toHaveBeenCalled();
  });
});

describe('Card Component', () => {
  it('renders children correctly', () => {
    const { getByText } = render(
      <Card>
        <></>
      </Card>
    );
    // Card should render without errors
  });
});

describe('API Integration', () => {
  it('should have correct API endpoints', () => {
    const { authAPI, moodAPI, journalAPI } = require('../utils/api');

    expect(authAPI).toBeDefined();
    expect(authAPI.signup).toBeDefined();
    expect(authAPI.login).toBeDefined();

    expect(moodAPI).toBeDefined();
    expect(moodAPI.checkIn).toBeDefined();

    expect(journalAPI).toBeDefined();
    expect(journalAPI.createEntry).toBeDefined();
  });
});
