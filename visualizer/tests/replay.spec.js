import {test, expect} from '@playwright/test';

test('RTL integer and load/store replay with navigation and memory', async ({page}) => {
  await page.goto('/');
  await expect(page.getByRole('heading', {name: 'CPU Execution Visualizer'})).toBeVisible();
  await expect(page.getByText('Cycle 1 / 8')).toBeVisible();
  await page.getByRole('button', {name: 'Next →'}).click();
  await expect(page.getByText('Cycle 2 / 8')).toBeVisible();
  await page.getByRole('button', {name: '← Previous'}).click();
  await expect(page.getByText('Cycle 1 / 8')).toBeVisible();

  await page.getByRole('combobox', {name: 'Program'}).selectOption('load_store');
  await expect(page.getByText('Cycle 1 / 11')).toBeVisible();
  await page.getByRole('button', {name: 'Next →'}).click();
  await expect(page.getByText('Cycle 2 / 11')).toBeVisible();
  await page.getByRole('button', {name: '↺ Reset'}).click();
  await expect(page.getByText('Cycle 1 / 11')).toBeVisible();
  await page.getByRole('slider', {name: 'Cycle'}).fill('10');
  await expect(page.getByText('Cycle 11 / 11')).toBeVisible();
  await expect(page.getByText('HALTED')).toBeVisible();
  await expect(page.getByRole('heading', {name: 'Memory after cycle'})).toBeVisible();
  await page.screenshot({path: 'artifacts/rvcore-load-store-visualizer.png', fullPage: true});
});
